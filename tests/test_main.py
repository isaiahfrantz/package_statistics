"""tests for package_statistics main()"""

import pytest
from package_statistics import *

def test_main():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        args = {}
        main(args)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

