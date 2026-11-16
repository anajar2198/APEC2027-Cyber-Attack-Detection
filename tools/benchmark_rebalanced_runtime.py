"""Measure completed-window CPU processing for the selected six-head detector.

This benchmarks recorded windows without sleeping between arrivals. It includes
preprocessing and output decoding, but not sensor acquisition/network transport
or attack-onset-to-alarm delay. No model training or threshold tuning occurs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import time


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--iterations',type=int,default=1000)
    parser.add_argument('--warmup',type=int,default=50)
    parser.add_argument('--threads',type=int,default=4)
    parser.add_argument('--report',type=Path,default=Path('paper_revision/results/rebalanced_runtime.json'))
    args=parser.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
    os.environ['TF_NUM_INTRAOP_THREADS']=str(args.threads)
    os.environ['TF_NUM_INTEROP_THREADS']='1'
    import csv
    import numpy as np
    import tensorflow as tf
    tf.config.threading.set_intra_op_parallelism_threads(args.threads)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    checkpoint=Path('architecture_results/balanced_multitask_20261115/01_balanced_finetune/best_composite.keras')
    stats_path=Path('architecture_results/multitask_20261113/preprocessing_and_split.npz')
    predictions_path=checkpoint.parent/'validation_predictions.npz'
    with np.load(stats_path,allow_pickle=False) as z:
        mean=z['mean']; std=z['std']
    with np.load(predictions_path,allow_pickle=False) as z:
        indices=z['indices'][:args.iterations].copy()
        reference={name.removeprefix('pred_'):z[name][:args.iterations].copy() for name in z.files if name.startswith('pred_')}
    print('Loading recorded benchmark windows...',flush=True)
    with np.load('cyber_dataset_FULL_MERGED.npz',allow_pickle=False) as z:
        features=z['X']
        windows=features[indices].copy()
        del features
    assert windows.shape==(args.iterations,128,16)
    def preprocess(raw):
        difference=np.diff(raw,axis=0,prepend=raw[:1])
        return ((np.concatenate([raw,difference],axis=-1)-mean)/std).astype(np.float32)[None,...]
    model=tf.keras.models.load_model(checkpoint,compile=False)
    @tf.function(input_signature=[tf.TensorSpec([1,128,32],tf.float32)],autograph=False)
    def infer(value):return model(value,training=False)
    def synchronize(outputs):return {name:value.numpy() for name,value in outputs.items()}
    def decode(p):
        attack=bool(p['attack'][0,0]>=.5)
        return dict(attack=attack,motor=int(np.argmax(p['motor'][0]))+1 if attack else 0,
            phases=(p['phases'][0]>=.5).astype(np.int32),
            severity=p['severity'][0]*.5,onset_present=bool(p['onset_present'][0,0]>=.5),
            onset_position=float(p['onset_position'][0,0]*127))
    start=time.perf_counter_ns()
    p=synchronize(infer(preprocess(windows[0])))
    first_call_ms=(time.perf_counter_ns()-start)/1e6
    for i in range(args.warmup):decode(synchronize(infer(preprocess(windows[i%len(windows)]))))
    print('Measuring',args.iterations,'batch-1 windows on CPU, all six heads...',flush=True)
    rows=[]; errors={name:0. for name in reference}
    for i,raw in enumerate(windows):
        t0=time.perf_counter_ns()
        value=preprocess(raw)
        t1=time.perf_counter_ns()
        p=synchronize(infer(value))
        t2=time.perf_counter_ns()
        decode(p)
        t3=time.perf_counter_ns()
        rows.append(dict(iteration=i,dataset_index=int(indices[i]),preprocessing_ms=(t1-t0)/1e6,
            inference_ms=(t2-t1)/1e6,decoding_ms=(t3-t2)/1e6,window_processing_ms=(t3-t0)/1e6))
        for name in reference:
            errors[name]=max(errors[name],float(np.max(np.abs(p[name][0]-reference[name][i]))))
    assert max(errors.values())<5e-5,errors
    def summary(key):
        values=np.array([r[key] for r in rows])
        return dict(mean_ms=float(values.mean()),median_ms=float(np.median(values)),
            p95_ms=float(np.percentile(values,95)),p99_ms=float(np.percentile(values,99)),
            minimum_ms=float(values.min()),maximum_ms=float(values.max()))
    cpu=next(line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name'))
    frequency=7.;length=128;stride=16
    budget_ms=1000*stride/frequency
    timings={key:summary(key) for key in ['preprocessing_ms','inference_ms','decoding_ms','window_processing_ms']}
    report=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),model='Selected epoch-45 rebalanced six-head CNN-BiGRU',
        checkpoint=str(checkpoint),checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        preprocessing_sha256=hashlib.sha256(stats_path.read_bytes()).hexdigest(),
        cpu=cpu,device='CPU only; no GPU',tensorflow=tf.__version__,python=platform.python_version(),
        numpy=np.__version__,platform=platform.platform(),intra_op_threads=args.threads,inter_op_threads=1,
        batch_size=1,iterations=args.iterations,warmup_iterations=args.warmup,
        synchronized_all_six_outputs=True,cold_first_call_including_tracing_ms=first_call_ms,
        timings=timings,output_maximum_absolute_errors_vs_saved_predictions=errors,
        assumed_feature_report_hz=frequency,rate_source='Author-confirmed approximately 7 Hz; not measured by this benchmark',
        window_length=length,stride=stride,nominal_window_duration_seconds=length/frequency,
        oldest_to_newest_sample_span_seconds=(length-1)/frequency,update_interval_seconds=stride/frequency,
        deadline_misses_observed=sum(r['window_processing_ms']>budget_ms for r in rows),
        median_processing_budget_utilization=timings['window_processing_ms']['median_ms']/budget_ms,
        p95_processing_speedup_vs_update_interval=budget_ms/timings['window_processing_ms']['p95_ms'],
        interpretation='Measured computational feasibility for a rolling-window schedule on this CPU, at the author-provided rate; not a hard-real-time guarantee or live end-to-end latency test',
        exclusions=['Dataset loading and model loading; first tracing call recorded separately',
            'Sensor feature extraction and feature report transport',
            'Network transmission, actuator response and worst-case scheduling guarantees',
            'Empirical attack-onset-to-first-correct-alarm delay'],
        detection_delay='Not measured here. Event-level delay requires verifying how window timestamps map to source samples and replaying every scheduled window in order. The random validation predictions omit intervening windows; window length/stride and onset-position MAE alone do not give first-correct-alarm latency.')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    with args.report.with_suffix('.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(dict(report=str(args.report),timings=timings,
        budget_ms=budget_ms,misses=report['deadline_misses_observed'],prediction_max_error=max(errors.values()))),flush=True)

if __name__=='__main__':main()
