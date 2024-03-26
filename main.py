import time
import numpy as np
from typing import List, Optional

import threading
import pandas as pd
import requests
import plotly.express as px

def generate_data() -> List[int]:
    """Generate some random data."""
    return np.random.randint(100, 10000, 1000).tolist()

def process1(data: List[int]) -> List[int]:
    """Find the next largest prime number for each number in the input list.

    Args:
        data: A list of integers.

    Returns:
        A list of the next largest prime numbers corresponding to each integer in the input list.
    """
    def foo(x):
        """Find the next largest prime number."""
        while True:
            x += 1
            if all(x % i for i in range(2, x)):
                return x
    return [foo(x) for x in data]

def process2(data: List[int]) -> List[int]:
    """Find the next perfect square greater than each number in the input list.

    Args:
        data: A list of integers.

    Returns:
        A list of the next perfect squares for each integer in the input list.
    """
    def foo(x):
        """check if number is perfect square."""
        while True:
            x += 1
            if int(np.sqrt(x)) ** 2 == x:
                return x
    return [foo(x) for x in data]

def final_process(data1: List[int], data2: List[int]) -> float:
    """Compute the mean of the differences between corresponding elements of two lists.

    Args:
        data1: A list of integers.
        data2: A list of integers.

    Returns:
        The mean difference between corresponding elements in the two lists.
    """
    return np.mean([x - y for x, y in zip(data1, data2)])

#Question 1: Under what circumstances do you think it will be worthwhile to offload one or both of 
#the processing tasks to your PC? And conversely, under what circumstances will it not be worthwhile?

#offload_url = 'http://192.168.242.1:5001'
offload_url = 'http://localhost:5001'


def run(offload: Optional[str] = None) -> float:
    """Run the program, offloading the specified function(s) to the server.
    
    Args:
        offload: Which function(s) to offload to the server. Can be None, 'process1', 'process2', or 'both'.

    Returns:
        float: the final result of the program.
    """
    data = generate_data()
    if offload is None: # in this case, we run the program locally
        data1 = process1(data)
        data2 = process2(data)
    elif offload == 'process1':
        data1 = None
        def offload_process1(data):
            nonlocal data1
            # TODO: Send a POST request to the server with the input data
            response = requests.post(f"{offload_url}/process1", json=data)
            data1 = response.json()
        thread = threading.Thread(target=offload_process1, args=(data,))
        thread.start()
        data2 = process2(data)
        thread.join()
        # Question 2: Why do we need to join the thread here?
        # Question 3: Are the processing functions executing in parallel or just concurrently? What is the difference?
        #   See this article: https://oxylabs.io/blog/concurrency-vs-parallelism
        #   ChatGPT is also good at explaining the difference between parallel and concurrent execution!
        #   Make sure to cite any sources you use to answer this question.
    elif offload == 'process2':
        data2 = None
        def offload_process2(data):
            nonlocal data2
            response = requests.post(f"{offload_url}/process2", json=data)
            data2 = response.json()
        thread = threading.Thread(target=offload_process2, args=(data,))
        thread.start()
        data1 = process1(data)
        thread.join()
    elif offload == 'both':
        def offload_process(data, process_name):
            response = requests.post(f"{offload_url}/{process_name}", json=data)
            return response.json()
        thread1 = threading.Thread(target=lambda: offload_process(data, "process1"))
        thread2 = threading.Thread(target=lambda: offload_process(data, "process2"))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        data1, data2 = thread1.result, thread2.result


    ans = final_process(data1, data2)
    return ans 

def main():
    rows = []
    samples = 5  # Change samples to 5 as per instructions
    modes = [None, 'process1', 'process2', 'both']  # Include all modes
    for mode in modes:
        times = []
        for i in range(samples):
            start = time.time()
            run(mode)
            end = time.time()
            times.append(end - start)
            print(f"Offloading {mode} - sample {i+1}: {times[-1]:.2f} seconds")
        rows.append([str(mode), np.mean(times), np.std(times)])

    df = pd.DataFrame(rows, columns=['Mode', 'Mean time', 'Std time'])

    # Plotting
    fig = px.bar(df, x='Mode', y='Mean time', error_y='Std time',
                 title='Execution Time by Offloading Mode',
                 labels={'Mean time': 'Mean Execution Time (s)', 'Mode': 'Offloading Mode'})
    fig.show()

    # Save plot
    fig.write_image("makespan.png")


    # Question 4: What is the best offloading mode? Why do you think that is?
    # Question 5: What is the worst offloading mode? Why do you think that is?
    # Question 6: The processing functions in the example aren't very likely to be used in a real-world application. 
    #   What kind of processing functions would be more likely to be used in a real-world application?
    #   When would you want to offload these functions to a server?
    
    
if __name__ == '__main__':
    main()
