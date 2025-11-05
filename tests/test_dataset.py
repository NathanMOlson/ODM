import unittest
import os
import shutil
import json
import tempfile

from opendm.photo import ODM_Photo
from opendm import config
from stages.dataset import ODMLoadDatasetStage


class TestDataset(unittest.TestCase):
    def setUp(self):
        pass

    def test_ignore_ypr_false(self):
        args = config.config("")
        dataset_dir = "tests/assets/datasets/single_image"
        tmp_dataset_dir = tempfile.mkdtemp()
        shutil.copytree(dataset_dir, tmp_dataset_dir, dirs_exist_ok=True)
        args.project_path = tmp_dataset_dir
        dataset = ODMLoadDatasetStage('dataset', args)
        outputs = {}
        dataset.process(args, outputs)
        with open(os.path.join(tmp_dataset_dir, "images.json"), mode="r",
                  encoding="utf-8") as f:
            image_list = json.load(f)
            self.assertEqual(len(image_list), 1)
            image_info = image_list[0]
        self.assertEqual(image_info["yaw"], 105.780071)
        self.assertEqual(image_info["pitch"], 40)
        self.assertEqual(image_info["roll"], 0)
        self.assertIsNotNone(image_info["omega"])
        self.assertIsNotNone(image_info["phi"])
        self.assertIsNotNone(image_info["kappa"])

        shutil.rmtree(tmp_dataset_dir)

    def test_ignore_ypr_true(self):
        args = config.config("")
        dataset_dir = "tests/assets/datasets/single_image"
        tmp_dataset_dir = tempfile.mkdtemp()
        shutil.copytree(dataset_dir, tmp_dataset_dir, dirs_exist_ok=True)
        args.project_path = tmp_dataset_dir
        args.ignore_ypr = True
        dataset = ODMLoadDatasetStage('dataset', args)
        outputs = {}
        dataset.process(args, outputs)
        with open(os.path.join(tmp_dataset_dir, "images.json"), mode="r",
                  encoding="utf-8") as f:
            image_list = json.load(f)
            self.assertEqual(len(image_list), 1)
            image_info = image_list[0]
        self.assertIsNone(image_info["yaw"])
        self.assertIsNone(image_info["pitch"])
        self.assertIsNone(image_info["roll"])
        self.assertIsNone(image_info["omega"])
        self.assertIsNone(image_info["phi"])
        self.assertIsNone(image_info["kappa"])

        shutil.rmtree(tmp_dataset_dir)
        

if __name__ == '__main__':
    unittest.main()