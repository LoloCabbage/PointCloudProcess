from laplace_interpolate import laplace
from step4 import step4
from step5 import step5
"""
default file has been put in the function
default resolution is 0.5m, for quick test, you can set it to 20m
"""
def test_(res = 20):
    laplace(res=res)
    step4(res=res)
    step5()
if __name__ == "__main__":
    test_()

