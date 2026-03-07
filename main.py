from pipeline import run_pipeline

prompt = input("Describe music: ")

music = run_pipeline(prompt)

print("Generated:", music)