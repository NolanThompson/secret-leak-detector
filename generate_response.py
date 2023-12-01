from gpt4all import GPT4All

#prompt LLM (NEEDS FINE TUNING)
def generate_response(prompt):
    model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
    output = model.generate(prompt, max_tokens=100)

    return(output)