import numpy as np
import base64
import timeit
import ast

def to_base64(array):
    # 将 NumPy 数组转换为 base64 字符串
    return base64.b64encode(array.tobytes()), array.shape, str(array.dtype)

def from_base64(encoded_str, shape, dtype):
    # 从 base64 字符串还原 NumPy 数组
    decoded_array = base64.b64decode(encoded_str)
    return np.frombuffer(decoded_array, dtype=np.dtype(dtype)).reshape(shape)

def to_string(array):
    # 将 NumPy 数组转换为字符串
    return str(array.tolist()), array.shape, str(array.dtype)

def from_string(string_str, shape, dtype):
    # 从字符串还原 NumPy 数组
    list_representation = ast.literal_eval(string_str)
    return np.array(list_representation).reshape(shape)

def test_performance():
    # 创建一个 NumPy 数组
    array = np.random.rand(1, 1024)

    # 使用 base64 进行序列化和反序列化
    base64_encoded, shape, dtype = to_base64(array)
    base64_time = timeit.timeit(lambda: from_base64(base64_encoded, shape, dtype), number=10)

    # 使用字符串进行序列化和反序列化
    string_encoded, _, _ = to_string(array)
    string_time = timeit.timeit(lambda: from_string(string_encoded, shape, dtype), number=10)

    print(f"Base64 serialization and deserialization took {base64_time:.4f} seconds.")
    print(f"String serialization and deserialization took {string_time:.4f} seconds.")

if __name__ == "__main__":
    test_performance()