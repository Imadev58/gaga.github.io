import time

def write_to_file():
    while True:
        with open('247.txt', 'a') as file:  # Open in append mode
            file.write('a\n')  # Write 'a' followed by a newline
        time.sleep(1)  # Wait for 1 second

if __name__ == "__main__":
    write_to_file()
