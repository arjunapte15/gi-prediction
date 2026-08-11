def test_imports():
    import pandas
    import sklearn
    import numpy

    assert pandas.__version__
    assert sklearn.__version__
    assert numpy.__version__
