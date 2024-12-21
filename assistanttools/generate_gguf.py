import subprocess
import os


def generate_gguf(llama_cpp_path, model_path, mmproj_path, image_path, prompt, temp):
    command = f"./{llama_cpp_path}llama-qwen2vl-cli -m {model_path} --mmproj {mmproj_path} --image {image_path} --temp {temp} -p {prompt}"
    print("Command: ", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    # print each output as it appears
    output = process.stdout.read().decode("utf-8")
    split_output = "per image patch)"
    vlm_output = output.split(split_output)[1]
    

    return vlm_output


def generate_gguf_stream(llama_cpp_path, model_path, mmproj_path, image_path, prompt, temp):
    command = f"./{llama_cpp_path}llama-qwen2vl-cli -m {model_path} --mmproj {mmproj_path} --image {image_path} --temp {temp} -p {prompt}"
    print("Command: ", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    # yield each output line as it appears
    for byte in iter(lambda: process.stdout.read(1), b''):
        try:
            yield byte.decode("utf-8")
        except UnicodeDecodeError:
            pass


if __name__ == '__main__':

    # take an image with the camera

    # os.system("libcamera-still -o image.jpg")
    temp = 0.
    prompt = '"What do you see?"'

    # output = generate_gguf(llama_cpp_path="../md-gguf/llama.cpp/",
    #                       model_path="../picorder-moondream2/moondream2-text-model.Q8.gguf",
    #                       mmproj_path="../md-gguf/moondream2/moondream2-mmproj-f16.gguf",
    #                       image_path="image.jpg",
    #                       prompt=prompt,
    #                       temp=0.)
    # print('--------------')
    # print(output)
    print("OUTPUT STREAM: ")
    vlm_output_start = "per image patch)"
    word = ""
    response = ""
    is_ready_to_print = False
    for line in generate_gguf_stream(llama_cpp_path="../llama.cpp/",  # without md-gguf for the vulkan version (not working)
                                          model_path="../llama.cpp/Qwen2-VL-2B-Instruct-Q4_K_M.gguf",
                                          mmproj_path="../llama.cpp/mmproj-Qwen2-VL-2B-Instruct-f16.gguf",
                                          image_path="images/image.jpg",
                                          prompt=prompt,
                                          temp=0.):
        # do not print lines until split_output
        response += line
        if vlm_output_start in response:
            # reset the word, and start printing
            response = ""
            is_ready_to_print = True
            print("READY TO PRINT")
        if is_ready_to_print:
            if ' ' in line:
                os.system(f"espeak '{word}'")
                word = ""
            else:
                word += line    
    os.system(f"espeak '{word}'")
    
    print("RESPONSE: ")
    print(response)

