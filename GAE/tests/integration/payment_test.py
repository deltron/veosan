from base import BaseTest
import unittest


class PaymentTest(BaseTest):
    def test_paypal_pdt_success(self):
        
        accept_url = "/provider/upgrade/success"
        get_string = "?tx=2EL01252P57277818&st=Pending&amt=9.99&cc=CAD&cm=ag5zfnZlb3Nhbi1zdGFnZXIPCxIIUHJvdmlkZXIYjicM&item_number=&sig=Baj3VVTp26kz8yR%2FW3mpMUIXsBxRB4Bxu7DMyW7NUm7LAh3QJH25LUg8UumcZGCoFPcaqNE0fHDKHrknapQPXlcsVNpLVQKicjnCQHzCg%2F1N4XxQQalkgpVBElkZhJQjqO7qO%2BypDgAmjb4XSWpyd5PSt9AmkNNWYIZmTvhGkA4%3D"