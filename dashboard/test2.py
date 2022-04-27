import torch
from instaloader import Post
from tqdm import tqdm
import torch.utils.data as data

import torchvision.datasets as datasets
import torchvision.transforms as transforms

from .utils import set_seed
from .phishingmodel import MobileNetClf


class ImageFolderWithPaths(datasets.ImageFolder):
    """Custom dataset that includes image file paths. Extends
    torchvision.datasets.ImageFolder
    """

    # override the __getitem__ method. this is the method that dataloader calls
    def __getitem__(self, index):
        # this is what ImageFolder normally returns
        original_tuple = super(ImageFolderWithPaths, self).__getitem__(index)
        # the image file path
        path = self.imgs[index][0]
        # make a new tuple that includes original and the path
        tuple_with_path = (original_tuple + (path,))
        return tuple_with_path


def main():

    set_seed(42)

    model = MobileNetClf()
    device = torch.device('cpu')
    model.load_state_dict(torch.load('models/best_model_resnet18.pt', map_location=device))

    img_size = 320
    pretrained_means = [0.485, 0.456, 0.406]
    pretrained_stds = [0.229, 0.224, 0.225]

    test_transforms = transforms.Compose([
        transforms.Resize(img_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean = pretrained_means,
            std = pretrained_stds)
    ])

    test_data = ImageFolderWithPaths(
        root = 'folder',
        transform = test_transforms)

    test_iterator = data.DataLoader(
        test_data,
        batch_size = 64)

    model.to(device)
    model.eval()
    preds, paths = [], []
    with torch.no_grad():
        for x, y, path in tqdm(test_iterator, desc='Eval'):
            x = x.to(device)
            y = y.to(device)

            preds += model(x).tolist()
            paths += path

    print(preds, paths)

if __name__ == '__main__':
    main()
