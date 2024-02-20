import subprocess

def run_script(script_name):
    subprocess.run(["python", script_name])

def main():
    scripts = ["binomial.py", "binary.py", "commander.py", "sequential.py", "product.py", "PyCSP.py"]
    for script in scripts:
        run_script(script)

if __name__ == "__main__":
    main()