from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def multThreads(func, argList, threads_num):
    print("threads_num:", threads_num)
    with ThreadPoolExecutor(max_workers=threads_num) as executor:
        results = list(
            tqdm(
                executor.map(func, argList),  # 直接传递 seqList 中的每个元素
                total=len(argList),
                desc="generating embeddings",
            )
        )
    return results
