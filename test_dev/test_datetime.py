from datetime import datetime, timedelta
from uuid import uuid4

date1 = datetime(2023, 2, 18)
date2 = date1 + timedelta(0, 3600)

date2str = str(date2)
print(date2str)

date3 = datetime.strptime(date2str, "%Y-%m-%d %H:%M:%S")

print(date3)


uuid_test = uuid4()
print(uuid_test)
print(str(uuid_test))
