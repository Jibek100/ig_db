import torch
import numpy as np

from torch.utils.data import Dataset
from tqdm import tqdm

from dashboard.model import DistilBertForSequenceClassification
from transformers import DistilBertConfig, DistilBertTokenizer
from sklearn.manifold import TSNE

TOKENIZER = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
DEVICE = torch.device("cpu")
MAX_SEQ_LENGTH = 256

class text_dataset(Dataset):
    def __init__(self, x, y=None, transform=None):
        self.x = x
        self.y = y
        self.transform = transform
        
    def __getitem__(self, index):
        tokenized_comment = TOKENIZER.tokenize(self.x[index])
        
        if len(tokenized_comment) > MAX_SEQ_LENGTH:
            tokenized_comment = tokenized_comment[:MAX_SEQ_LENGTH]
            
        ids_review  = TOKENIZER.convert_tokens_to_ids(tokenized_comment)
        padding = [0] * (MAX_SEQ_LENGTH - len(ids_review))
        ids_review += padding
        
        assert len(ids_review) == MAX_SEQ_LENGTH
        
        ids_review = torch.tensor(ids_review)
        if self.y is None:
            return ids_review 

        hcc = self.y[index] # toxic comment        
        list_of_labels = [torch.from_numpy(hcc)]

        return ids_review, list_of_labels[0]
    
    def __len__(self):
        return len(self.x)


def preds(model, test_loader):
    predictions = []
    for inputs in test_loader:
        inputs = inputs.to(DEVICE) 
        with torch.no_grad():
            outputs = model(inputs)
            outputs = torch.sigmoid(outputs)
            if len(outputs) > 1:
                predictions += outputs.cpu().detach().numpy().tolist()
            else:
                predictions.append(outputs.cpu().detach().numpy().tolist())

    return predictions

def text_to_2d_plane(model, test_loader):
    embeds = []
    for inputs in tqdm(test_loader, total=len(test_loader)):
        inputs = inputs.to(DEVICE)
        with torch.no_grad():
            outputs = model.distilbert(inputs)
            if len(outputs) > 1:
                embeds += outputs[0][:, 0].squeeze().tolist()
            else:
                embeds.append(outputs[0][:, 0].squeeze().tolist())
            # embeds.append(outputs[0][:, 0].squeeze().tolist())
    return TSNE().fit_transform(embeds)

def main():
    config = DistilBertConfig(
        vocab_size=32000, hidden_dim=768,
        dropout=0.1, num_labels=6,
        n_layers=12, n_heads=12,
        intermediate_size=3072)
    state_dict = torch.load('models/distilbert_model_weights.pth', map_location=DEVICE)
    model = DistilBertForSequenceClassification(config)
    model.load_state_dict(state_dict=state_dict)
    model.to(DEVICE)
    comments = ['Fuck u', 'I like u', 'I hate u', 'I wish u were dead!',
    'U r a good man', 'I hope that you will die someday', 'Hate must be vanished',
    'Fuck yeah', 'Fucking aweasome', 'The government should have done somethinng more meaningful' ]
    test_dataset = text_dataset(comments)
    prediction_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=2, shuffle=False)
    planes = text_to_2d_plane(model=model, test_loader=prediction_dataloader)
    print(planes)


if __name__ == '__main__':
    main()
