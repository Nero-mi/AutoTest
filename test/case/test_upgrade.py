import pytest
import allure
from test.api import Upgrade


@allure.feature('Upgrade Test')
class Test_Upgrade:
    @allure.story('upgrade_t1')
    def test_demo1(self):
        test1 = Upgrade.Board_Test()
        test1.Upgrade()
        print("test1")
        assert False

    def test_demo2(self):
        print("test2")
        assert True

        