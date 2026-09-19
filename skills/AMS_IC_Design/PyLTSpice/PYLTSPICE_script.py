import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from PyLTSpice import SimRunner, RawRead

# 1. Start the simulation runner
runner = SimRunner(output_folder='./temp', verbose=True)

# 2. Automatically detect any .asc schematic files in the script folder
asc_files = glob.glob("*.asc")

if not asc_files:
    print("No .asc schematic files found in this folder!")
else:
    for asc_filename in asc_files:
        print(f"Simulating and analyzing: {asc_filename}...")
        
        try:
            runner.run(asc_filename)
            base_name = os.path.splitext(asc_filename)[0]
            
            # 3. Find the generated .raw file inside the temp folder
            search_pattern = os.path.join('./temp', f"{base_name}*.raw")
            generated_raw_files = glob.glob(search_pattern)
            
            if generated_raw_files:
                raw_filename = max(generated_raw_files, key=os.path.getmtime)
                raw_data = RawRead(raw_filename)
                
                # 4. FIXED: Added .get_wave() to pull raw numeric numpy arrays
                frequencies = np.abs(raw_data.get_trace('frequency').get_wave())
                v_out = raw_data.get_trace('V(out)').get_wave()
                v_in = raw_data.get_trace('V(n001)').get_wave()
                
                # Calculate explicit Gain Magnitude in dB safely using numeric arrays
                gain_db = 20 * np.log10(np.abs(v_out / v_in))
                
                # --- ADVANCED PYTHON DATA PROCESSING ---
                
                # Find maximum gain (passband gain baseline)
                max_gain = np.max(gain_db)
                target_cutoff_gain = max_gain - 3.01
                
                # Linearly interpolate the exact -3dB cutoff frequency point
                cutoff_freq = np.interp(target_cutoff_gain, gain_db[::-1], frequencies[::-1])
                
                # Calculate the exact Roll-Off Slope (dB/Decade) using the last data decade
                f_high = frequencies[-1]
                f_low = frequencies[-1] / 10.0
                gain_f_high = gain_db[-1]
                gain_f_low = np.interp(f_low, frequencies, gain_db)
                slope_db_per_decade = (gain_f_high - gain_f_low) / np.log10(f_high / f_low)
                
                # 5. Generate Advanced Plot Figure
                fig, ax = plt.subplots(figsize=(11, 7))
                
                # Plot the raw simulation curve
                ax.semilogx(frequencies, gain_db, label='Simulated Response', color='blue', linewidth=2.5)
                
                # Add the computed -3dB Cutoff marker point
                ax.plot(cutoff_freq, target_cutoff_gain, 'ro', markersize=8, label='Computed Cutoff Point')
                
                # Draw dynamic dotted guide lines to the axes intersections
                ax.axvline(x=cutoff_freq, color='red', linestyle=':', alpha=0.7)
                ax.axhline(y=target_cutoff_gain, color='red', linestyle=':', alpha=0.7)
                
                # Place an informative text data box directly onto the chart area
                info_text = (
                    f"ANALYSIS RESULTS:\n"
                    f"• Max Passband Gain: {max_gain:.2f} dB\n"
                    f"• Exact Cutoff (-3dB): {cutoff_freq:.1f} Hz\n"
                    f"• Roll-Off Rate: {slope_db_per_decade:.1f} dB/decade"
                )
                props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
                ax.text(0.05, 0.25, info_text, transform=ax.transAxes, fontsize=11, verticalalignment='top', bbox=props)
                
                # Annotate the specific cutoff coordinate dot with an arrow indicator
                ax.annotate(f'-3dB Point ({cutoff_freq:.1f} Hz)', 
                            xy=(cutoff_freq, target_cutoff_gain), 
                            xytext=(cutoff_freq * 2.5, target_cutoff_gain + 5),
                            arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6))
                
                # Format axis grids and titles
                ax.set_title(f'Advanced Filter Diagnostics: {asc_filename}', fontsize=12, fontweight='bold')
                ax.set_xlabel('Frequency (Hz)', fontsize=10)
                ax.set_ylabel('Gain Magnitude (dB)', fontsize=10)
                ax.grid(True, which="both", linestyle="--", linewidth=0.5)
                ax.legend(loc='upper right')
                
                # Export figure to working directory
                plot_filename = f"{base_name}_advanced_diagnostics.png"
                plt.savefig(plot_filename, dpi=300)
                print(f"Analysis complete. Extended figure saved to: {plot_filename}")
                plt.show()
                
            else:
                print(f"LTspice finished but no raw file found matching pattern: {search_pattern}\n")
                
        except Exception as e:
            print(f"Failed to analyze {asc_filename}. Error details: {e}\n")
