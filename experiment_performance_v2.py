#!/usr/bin/env python3
"""
RSA Digital Signature Performance Experiment

Measures and compares execution times of signing and verification
with different RSA key sizes (512, 1024, 2048, 4096 bits).

Experiment Design:
- Test file: 5MB random binary data
- Key sizes: 512, 1024, 2048, 4096 bits
- Runs per config: 10 iterations
- Metrics: Average time, standard deviation, min/max
- Output: Table, analysis, optional charts
"""

import os
import json
import time
import statistics
import io
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Try to import matplotlib (optional)
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from core.rsa_logic import generate_keys, sign_data, verify_signature
from core.file_handler import read_file, write_signature, read_signature


class RSAPerformanceExperiment:
    """Manages performance measurement experiments"""
    
    def __init__(self, test_file_size_mb: int = 5, num_runs: int = 10):
        self.test_file_size_mb = test_file_size_mb
        self.num_runs = num_runs
        self.key_sizes = [512, 1024, 2048, 4096]  # Supported by the code
        self.output_dir = Path("experiment_results")
        self.output_dir.mkdir(exist_ok=True)
        self.test_file = None
        self.results = {}
    
    def suppress_output(self, func, *args):
        """Execute function and suppress print output"""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            result = func(*args)
            return result
        finally:
            sys.stdout = old_stdout
    
    def create_test_file(self):
        """Create 5MB test file"""
        print(f"\n{'='*70}")
        print(f"Creating {self.test_file_size_mb}MB test file...")
        print(f"{'='*70}")
        
        file_path = self.output_dir / f"test_file_{self.test_file_size_mb}mb.bin"
        
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✓ Using existing test file: {file_path} ({size_mb:.2f} MB)")
            self.test_file = str(file_path)
            return
        
        print(f"Generating random binary data...")
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = self.test_file_size_mb * 1024 * 1024
        
        with open(file_path, 'wb') as f:
            written = 0
            while written < total_size:
                chunk = os.urandom(min(chunk_size, total_size - written))
                f.write(chunk)
                written += len(chunk)
                pct = (written / total_size) * 100
                print(f"  Progress: {pct:.0f}%", end='\r')
        
        print(f"✓ Test file created: {file_path}\n")
        self.test_file = str(file_path)
    
    def run_experiment(self):
        """Run the complete experiment"""
        print("\n" + "="*70)
        print("RSA DIGITAL SIGNATURE PERFORMANCE EXPERIMENT")
        print("="*70)
        print(f"Test File Size: {self.test_file_size_mb}MB")
        print(f"Runs per Config: {self.num_runs}")
        print(f"Key Sizes: {', '.join(str(ks) + '-bit' for ks in self.key_sizes)}")
        
        # Create test file
        self.create_test_file()
        
        # Load test data
        test_data = read_file(self.test_file)
        
        # Run experiments
        print(f"\n{'='*70}")
        print("Running Performance Measurements")
        print(f"{'='*70}\n")
        
        for key_size in self.key_sizes:
            print(f"Testing {key_size}-bit RSA...")
            
            # Generate keys (suppress output)
            print(f"  Generating keys...", end='', flush=True)
            private_key, public_key = self.suppress_output(generate_keys, key_size)
            print(" ✓")
            
            # Measure signing
            print(f"  Measuring signing ({self.num_runs} runs)...", end='', flush=True)
            signing_times = []
            signature = None
            
            for i in range(self.num_runs):
                start = time.perf_counter()
                signature = self.suppress_output(sign_data, test_data, private_key)
                elapsed = time.perf_counter() - start
                signing_times.append(elapsed)
            
            print(" ✓")
            
            # Save signature for verification
            sig_file = self.output_dir / f"sig_{key_size}bit.bin"
            write_signature(str(sig_file), signature)
            
            # Measure verification
            print(f"  Measuring verification ({self.num_runs} runs)...", end='', flush=True)
            verification_times = []
            
            for i in range(self.num_runs):
                start = time.perf_counter()
                result = self.suppress_output(verify_signature, test_data, signature, public_key)
                elapsed = time.perf_counter() - start
                verification_times.append(elapsed)
            
            print(" ✓")
            
            # Store results
            self.results[key_size] = {
                "signing": signing_times,
                "verification": verification_times,
                "signing_stats": self._stats(signing_times),
                "verification_stats": self._stats(verification_times),
                "sig_file": str(sig_file)
            }
        
        # Generate reports
        self._generate_table()
        self._generate_analysis()
        if HAS_MATPLOTLIB:
            self._generate_charts()
        
        print(f"\n{'='*70}")
        print("✓ EXPERIMENT COMPLETE")
        print(f"{'='*70}")
        print(f"Results saved to: {self.output_dir}/")
        print(f"\nGenerated files:")
        print(f"  - results_table.txt")
        print(f"  - analysis.txt")
        if HAS_MATPLOTLIB:
            print(f"  - performance_chart.png")
    
    def _stats(self, data: List[float]) -> Dict:
        """Calculate statistics for timing data"""
        return {
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "stdev": statistics.stdev(data) if len(data) > 1 else 0,
            "min": min(data),
            "max": max(data),
        }
    
    def _generate_table(self):
        """Generate results table"""
        table_path = self.output_dir / "results_table.txt"
        
        with open(table_path, 'w') as f:
            f.write("\n" + "="*100 + "\n")
            f.write("RSA DIGITAL SIGNATURE PERFORMANCE RESULTS\n")
            f.write("="*100 + "\n\n")
            
            f.write(f"Test File Size: {self.test_file_size_mb}MB | Runs per Config: {self.num_runs}\n\n")
            
            # Signing times
            f.write("SIGNING TIME (seconds)\n")
            f.write("-"*100 + "\n")
            f.write(f"{'Key Size':<15} {'Mean':<15} {'Median':<15} {'StDev':<15} {'Min':<15} {'Max':<15}\n")
            f.write("-"*100 + "\n")
            
            for ks in self.key_sizes:
                s = self.results[ks]["signing_stats"]
                f.write(f"{ks}-bit{'':<10} {s['mean']:<15.6f} {s['median']:<15.6f} {s['stdev']:<15.6f} {s['min']:<15.6f} {s['max']:<15.6f}\n")
            
            f.write("\n")
            
            # Verification times
            f.write("VERIFICATION TIME (seconds)\n")
            f.write("-"*100 + "\n")
            f.write(f"{'Key Size':<15} {'Mean':<15} {'Median':<15} {'StDev':<15} {'Min':<15} {'Max':<15}\n")
            f.write("-"*100 + "\n")
            
            for ks in self.key_sizes:
                v = self.results[ks]["verification_stats"]
                f.write(f"{ks}-bit{'':<10} {v['mean']:<15.6f} {v['median']:<15.6f} {v['stdev']:<15.6f} {v['min']:<15.6f} {v['max']:<15.6f}\n")
            
            f.write("\n")
            
            # Combined times
            f.write("COMBINED TIME (Signing + Verification)\n")
            f.write("-"*100 + "\n")
            f.write(f"{'Key Size':<15} {'Total Mean':<15} {'Ratio vs 512-bit':<20}\n")
            f.write("-"*100 + "\n")
            
            baseline = self.results[512]["signing_stats"]["mean"] + self.results[512]["verification_stats"]["mean"]
            
            for ks in self.key_sizes:
                s_mean = self.results[ks]["signing_stats"]["mean"]
                v_mean = self.results[ks]["verification_stats"]["mean"]
                total = s_mean + v_mean
                ratio = total / baseline
                f.write(f"{ks}-bit{'':<10} {total:<15.6f} {ratio:.2f}x\n")
        
        print(f"✓ Results table: {table_path}")
    
    def _generate_analysis(self):
        """Generate analysis report"""
        analysis_path = self.output_dir / "analysis.txt"
        
        with open(analysis_path, 'w') as f:
            f.write("\n" + "="*100 + "\n")
            f.write("RSA DIGITAL SIGNATURE PERFORMANCE ANALYSIS\n")
            f.write("="*100 + "\n\n")
            
            f.write("1. EXPERIMENT SETUP\n")
            f.write("-"*100 + "\n")
            f.write(f"Test File Size:      {self.test_file_size_mb}MB\n")
            f.write(f"Key Sizes Tested:    512, 1024, 2048, 4096 bits\n")
            f.write(f"Iterations:          {self.num_runs} per configuration\n")
            f.write(f"Total Operations:    {len(self.key_sizes) * 2 * self.num_runs}\n\n")
            
            f.write("2. KEY FINDINGS\n")
            f.write("-"*100 + "\n\n")
            
            # Performance comparison
            baseline_sign = self.results[512]["signing_stats"]["mean"]
            baseline_verify = self.results[512]["verification_stats"]["mean"]
            
            f.write("Signing Time Comparison (vs 512-bit baseline):\n")
            for ks in self.key_sizes:
                mean = self.results[ks]["signing_stats"]["mean"]
                ratio = mean / baseline_sign
                f.write(f"  {ks:4d}-bit: {mean:10.6f}s ({ratio:6.1f}x slower)\n")
            
            f.write("\nVerification Time Comparison (vs 512-bit baseline):\n")
            for ks in self.key_sizes:
                mean = self.results[ks]["verification_stats"]["mean"]
                ratio = mean / baseline_verify
                f.write(f"  {ks:4d}-bit: {mean:10.6f}s ({ratio:6.1f}x slower)\n")
            
            f.write("\n3. PERFORMANCE CHARACTERISTICS\n")
            f.write("-"*100 + "\n\n")
            
            f.write("Time Complexity:\n")
            f.write("  RSA operations have O(n³) time complexity relative to key bit length.\n")
            f.write("  Doubling key size roughly multiplies execution time by 8-10x.\n\n")
            
            f.write("Variability Analysis (Coefficient of Variation):\n")
            for ks in self.key_sizes:
                s_mean = self.results[ks]["signing_stats"]["mean"]
                s_stdev = self.results[ks]["signing_stats"]["stdev"]
                v_mean = self.results[ks]["verification_stats"]["mean"]
                v_stdev = self.results[ks]["verification_stats"]["stdev"]
                
                s_cv = (s_stdev / s_mean * 100) if s_mean > 0 else 0
                v_cv = (v_stdev / v_mean * 100) if v_mean > 0 else 0
                
                f.write(f"  {ks}-bit: Signing ±{s_cv:.2f}%, Verification ±{v_cv:.2f}%\n")
            
            f.write("\n4. SECURITY VS PERFORMANCE TRADE-OFFS\n")
            f.write("-"*100 + "\n\n")
            
            f.write("512-bit RSA:\n")
            f.write("  • Security: CRITICALLY WEAK (broken)\n")
            f.write("  • Speed: Fastest baseline\n")
            f.write("  • Verdict: NEVER USE - only for educational demonstrations\n\n")
            
            f.write("1024-bit RSA:\n")
            f.write("  • Security: DEPRECATED (factored with significant resources)\n")
            f.write("  • Speed: ~{:.0f}x-{:.0f}x slower than 512-bit\n".format(
                    self.results[1024]["signing_stats"]["mean"] / baseline_sign,
                    self.results[1024]["verification_stats"]["mean"] / baseline_verify))
            f.write("  • Verdict: AVOID - only for legacy compatibility\n\n")
            
            f.write("2048-bit RSA:\n")
            f.write("  • Security: ADEQUATE (NIST SP 800-56B until 2030+)\n")
            f.write("  • Speed: ~{:.0f}x slower than 512-bit\n".format(
                    self.results[2048]["signing_stats"]["mean"] / baseline_sign))
            f.write("  • Verdict: RECOMMENDED for general-purpose use\n")
            f.write("  • Use Cases: TLS certificates, digital signatures, email signing\n\n")
            
            f.write("4096-bit RSA:\n")
            f.write("  • Security: STRONG (future-proof, recommended for long-term)\n")
            f.write("  • Speed: ~{:.0f}x slower than 512-bit\n".format(
                    self.results[4096]["signing_stats"]["mean"] / baseline_sign))
            f.write("  • Verdict: RECOMMENDED for high-security applications\n")
            f.write("  • Use Cases: Government, finance, critical infrastructure\n\n")
            
            f.write("5. RECOMMENDATIONS\n")
            f.write("-"*100 + "\n\n")
            
            f.write("For Production Systems:\n")
            f.write("  ✓ Default choice: 2048-bit RSA (balance security & performance)\n")
            f.write("  ✓ High-security: 4096-bit RSA if long-term protection needed\n")
            f.write("  ✗ Never: 512 or 1024-bit for new systems\n\n")
            
            f.write("Performance Optimization:\n")
            f.write("  • Pre-generate keys and cache them\n")
            f.write("  • Defer signing to background threads for large batches\n")
            f.write("  • Consider hardware acceleration (TPM, HSM) for production\n")
            f.write("  • Profile your application to identify bottlenecks\n\n")
            
            f.write("6. CONCLUSIONS\n")
            f.write("-"*100 + "\n\n")
            f.write("✓ RSA signing/verification times scale cubically with key size\n")
            f.write("✓ The performance penalty for 2048-bit vs 512-bit is acceptable\n")
            f.write("✓ 2048-bit is the minimum recommended for new implementations\n")
            f.write("✓ 4096-bit should be used for systems requiring 30+ year security\n")
            f.write("✓ Performance is rarely the limiting factor in practice\n")
        
        print(f"✓ Analysis report: {analysis_path}")
    
    def _generate_charts(self):
        """Generate performance visualization charts"""
        
        print(f"✓ Generating charts...")
        
        # Prepare data
        key_sizes = self.key_sizes
        signing_means = [self.results[ks]["signing_stats"]["mean"] for ks in key_sizes]
        signing_stdevs = [self.results[ks]["signing_stats"]["stdev"] for ks in key_sizes]
        verification_means = [self.results[ks]["verification_stats"]["mean"] for ks in key_sizes]
        verification_stdevs = [self.results[ks]["verification_stats"]["stdev"] for ks in key_sizes]
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('RSA Digital Signature Performance Analysis', fontsize=16, fontweight='bold')
        
        # Chart 1: Bar comparison
        ax = axes[0, 0]
        x = np.arange(len(key_sizes))
        width = 0.35
        
        ax.bar(x - width/2, signing_means, width, label='Signing', yerr=signing_stdevs, capsize=5)
        ax.bar(x + width/2, verification_means, width, label='Verification', yerr=verification_stdevs, capsize=5)
        ax.set_xlabel('RSA Key Size')
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Signing vs Verification Time')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{ks}-bit' for ks in key_sizes])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Chart 2: Total combined time
        ax = axes[0, 1]
        total_means = [signing_means[i] + verification_means[i] for i in range(len(key_sizes))]
        colors = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60']
        
        bars = ax.bar(range(len(key_sizes)), total_means, color=colors)
        for i, (bar, val) in enumerate(zip(bars, total_means)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}s', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('RSA Key Size')
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Total Operation Time (Signing + Verification)')
        ax.set_xticks(range(len(key_sizes)))
        ax.set_xticklabels([f'{ks}-bit' for ks in key_sizes])
        ax.grid(axis='y', alpha=0.3)
        
        # Chart 3: Scaling curve (log scale)
        ax = axes[1, 0]
        ax.plot(key_sizes, signing_means, marker='o', linewidth=2, markersize=8, label='Signing')
        ax.plot(key_sizes, verification_means, marker='s', linewidth=2, markersize=8, label='Verification')
        ax.set_xlabel('RSA Key Size (bits)')
        ax.set_ylabel('Time (seconds, log scale)')
        ax.set_title('Performance Scaling (Logarithmic)')
        ax.set_yscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3, which='both')
        
        # Chart 4: Speedup relative to 512-bit
        ax = axes[1, 1]
        baseline_total = signing_means[0] + verification_means[0]
        speedup_ratios = []
        
        for i in range(len(key_sizes)):
            total = signing_means[i] + verification_means[i]
            ratio = total / baseline_total
            speedup_ratios.append(ratio)
        
        bars = ax.barh(range(len(key_sizes)), speedup_ratios, color=colors)
        for i, (bar, ratio) in enumerate(zip(bars, speedup_ratios)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{ratio:.1f}x', ha='left', va='center', fontweight='bold', fontsize=10)
        
        ax.set_yticks(range(len(key_sizes)))
        ax.set_yticklabels([f'{ks}-bit' for ks in key_sizes])
        ax.set_xlabel('Slowdown Factor (vs 512-bit)')
        ax.set_title('Relative Performance (512-bit = baseline)')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        chart_path = self.output_dir / "performance_chart.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"✓ Chart saved: {chart_path}")
        plt.close()


def main():
    try:
        experiment = RSAPerformanceExperiment(test_file_size_mb=5, num_runs=10)
        experiment.run_experiment()
    except Exception as e:
        print(f"\n✗ Experiment failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
