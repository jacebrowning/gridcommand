from app import constants


def test_generate_code():
    code = constants.generate_code()
    assert len(code) == 4
