import json

import service_name.messages.test_pb2 as test_pb2

testMes = test_pb2.TestMessage()

dictionary: dict = {
    "var1": "val1",
    "var2": "val2",
    "var3": {"var4": "val4", "var5": "val5"},
}

testMes.int_var = 5
testMes.float_var = 5.25
testMes.str_var = "hello"
testMes.bool_var = True

testMes.dict_var = json.dumps(dictionary)

testMes.list_int_var.extend([3, 2, 1])
testMes.list_str_var.extend(["str1", "str2", "str3"])
testMes.list_float_var.extend([3.3, 2.2, -1.1])
testMes.list_bool_var.extend([True, False, False])

serialized_string = testMes.SerializeToString()

newTestMes = test_pb2.TestMessage()
newTestMes.ParseFromString(serialized_string)

dict1: dict = json.loads(newTestMes.dict_var)

print(dict1["var3"]["var4"])
print(newTestMes.list_float_var)
print(newTestMes.list_float_var[1])
print(newTestMes.list_str_var[2])
