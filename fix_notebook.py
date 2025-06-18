#!/usr/bin/env python3
"""
Fix the malformed ithaka_master_notebook.ipynb
"""

import json
import sys

def fix_notebook():
    # Read the backup file
    with open('/home/teocasares/ithaka-powertrain-sim/notebooks/ithaka_master_notebook_backup.ipynb', 'r') as f:
        content = f.read()
    
    # The file is truncated and has a malformed ending. 
    # We need to reconstruct the proper JSON structure
    
    # Find where the good content ends (before the malformed part)
    # Look for the last complete cell
    lines = content.split('\n')
    
    # Find the line with 'display(export_widget)' and reconstruct from there
    good_lines = []
    in_source = False
    
    for i, line in enumerate(lines):
        if 'display(export_widget)' in line and '"' in line:
            # This is the last line of the code cell
            good_lines.append(line)
            # Add proper cell closure
            good_lines.append('   ]')
            good_lines.append('  },')
            good_lines.append('  {')
            good_lines.append('   "cell_type": "markdown",')
            good_lines.append('   "metadata": {},')
            good_lines.append('   "source": [')
            good_lines.append('    "## 🎉 Congratulations!\\n",')
            good_lines.append('    "\\n",')
            good_lines.append('    "You\'ve successfully designed and simulated your motorcycle powertrain! \\n",')
            good_lines.append('    "\\n",')
            good_lines.append('    "**What you accomplished:**\\n",')
            good_lines.append('    "- ⚙️ Selected optimal components for your use case\\n",')
            good_lines.append('    "- 🗺️ Tested performance on realistic routes\\n",')
            good_lines.append('    "- 📊 Analyzed comprehensive simulation results\\n",')
            good_lines.append('    "- 📄 Generated professional reports\\n",')
            good_lines.append('    "\\n",')
            good_lines.append('    "**Next steps:**\\n",')
            good_lines.append('    "- Try different component combinations\\n",')
            good_lines.append('    "- Test various route types\\n",')
            good_lines.append('    "- Optimize for your specific requirements\\n",')
            good_lines.append('    "- Export results for presentations\\n",')
            good_lines.append('    "\\n",')
            good_lines.append('    "*Happy powertrain designing!* 🚀"')
            good_lines.append('   ]')
            good_lines.append('  }')
            good_lines.append(' ],')
            good_lines.append(' "metadata": {')
            good_lines.append('  "kernelspec": {')
            good_lines.append('   "display_name": "Python 3",')
            good_lines.append('   "language": "python",')
            good_lines.append('   "name": "python3"')
            good_lines.append('  },')
            good_lines.append('  "language_info": {')
            good_lines.append('   "codemirror_mode": {')
            good_lines.append('    "name": "ipython",')
            good_lines.append('    "version": 3')
            good_lines.append('   },')
            good_lines.append('   "file_extension": ".py",')
            good_lines.append('   "mimetype": "text/x-python",')
            good_lines.append('   "name": "python",')
            good_lines.append('   "nbconvert_exporter": "python",')
            good_lines.append('   "pygments_lexer": "ipython3",')
            good_lines.append('   "version": "3.8.0"')
            good_lines.append('  },')
            good_lines.append('  "colab": {')
            good_lines.append('   "provenance": []')
            good_lines.append('  }')
            good_lines.append(' },')
            good_lines.append(' "nbformat": 4,')
            good_lines.append(' "nbformat_minor": 0')
            good_lines.append('}')
            break
        else:
            good_lines.append(line)
    
    # Write the fixed notebook
    fixed_content = '\n'.join(good_lines)
    
    with open('/home/teocasares/ithaka-powertrain-sim/notebooks/ithaka_master_notebook.ipynb', 'w') as f:
        f.write(fixed_content)
    
    # Validate the JSON
    try:
        with open('/home/teocasares/ithaka-powertrain-sim/notebooks/ithaka_master_notebook.ipynb', 'r') as f:
            json.load(f)
        print("✅ Notebook fixed successfully and is valid JSON!")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON validation failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_notebook()
    sys.exit(0 if success else 1)