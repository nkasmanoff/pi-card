import subprocess
import os


def generate_gguf(llama_cpp_path, model_path, mmproj_path, image_path, prompt, temp):
    command = f"./{llama_cpp_path}llava-cli -m {model_path} --mmproj {mmproj_path} --image {image_path} --temp {temp} -p {prompt} -c 26 --mlock"
    print("Command: ", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    # print each output as it appears
    output = process.stdout.read().decode("utf-8")
    return output


def generate_gguf_stream(llama_cpp_path, model_path, mmproj_path, image_path, prompt, temp):
    command = f"./{llama_cpp_path}llava-cli --no-mmap -m {model_path} --mmproj {mmproj_path} --image {image_path} --temp {temp} -p {prompt}"
    print("Command: ", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    # yield each output line as it appears
    for byte in iter(lambda: process.stdout.read(1), b''):
        yield byte.decode("utf-8")


if __name__ == '__main__':

    # take an image with the camera

    # os.system("libcamera-still -o image.jpg")
    temp = 0.
    prompt = '"<image>\n\nQuestion: What do you see?\n\nAnswer: "'

    # output = generate_gguf(llama_cpp_path="../md-gguf/llama.cpp/",
    #                       model_path="../picorder-moondream2/moondream2-text-model.Q8.gguf",
    #                       mmproj_path="../md-gguf/moondream2/moondream2-mmproj-f16.gguf",
    #                       image_path="image.jpg",
    #                       prompt=prompt,
    #                       temp=0.)
    # print('--------------')
    # print(output)
    for line in generate_gguf_stream(llama_cpp_path="../md-gguf/llama.cpp/",
                                     model_path="../picorder-moondream2/moondream2-text-model.Q8.gguf",
                                     mmproj_path="../md-gguf/moondream2/moondream2-mmproj-f16.gguf",
                                     image_path="images/image.jpg",
                                     prompt=prompt,
                                     temp=0.):
        if ' ' in line:
            print('--------------')
        print(line, end='', flush=True)
