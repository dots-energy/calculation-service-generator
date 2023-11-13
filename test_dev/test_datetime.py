#  This work is based on original code developed and copyrighted by TNO 2023.
#  Subsequent contributions are licensed to you by the developers of such code and are
#  made available to the Project under one or several contributor license agreements.
#
#  This work is licensed to you under the Apache License, Version 2.0.
#  You may obtain a copy of the license at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Contributors:
#      TNO         - Initial implementation
#  Manager:
#      TNO

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
