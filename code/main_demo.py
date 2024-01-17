from step4 import step4

"""
default file has been put in the function
default resolution is 0.5m, for quick test, you can set it to 10m
"""
def test_(res = 5):
    veg_dsm = step4(res=res)

if __name__ == "__main__":
    test_()

