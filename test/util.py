from unittest import TestCase
import os
import shutil


this_dir = os.path.realpath(os.path.dirname(__file__))


class Test(TestCase):

    scratch_dir = os.path.join(this_dir, 'scratch')


    def setUp(self):
        if not os.path.isdir(self.scratch_dir):
            os.mkdir(self.scratch_dir)


    def tearDown(self):
        self.delete_scratch()


    def delete_scratch(self):
        if os.path.isdir(self.scratch_dir):
            shutil.rmtree(self.scratch_dir)


    def assertRaises(self, cls, f, *args, **kwargs):
        try:
            f(*args, **kwargs)
        except cls, e:
            return e.message
        else:
            name = cls.__name__ if hasattr(cls, '__name__') else str(cls)
            raise self.failureException, "%s not raised" % name


