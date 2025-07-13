# tests/unit/test_repository.py
def test_save_and_get_passenger(passenger_repository):
    """
    Testa se o repositório salva e recupera um item corretamente.
    """
    passenger_id = "test-id-123"
    item_to_save = {
        'id': passenger_id,
        'probability': '0.75',
        'input_data': {'Age': 30}
    }

    passenger_repository.save(item_to_save)

    retrieved_item = passenger_repository.get_by_id(passenger_id)

    assert retrieved_item is not None
    assert retrieved_item['id'] == passenger_id
    assert retrieved_item['input_data']['Age'] == 30

def test_get_all_passengers(passenger_repository):
    """
    Testa se o repositório lista todos os itens corretamente.
    """
    item1 = {'id': 'id1', 'probability': '0.1'}
    item2 = {'id': 'id2', 'probability': '0.2'}

    passenger_repository.save(item1)
    passenger_repository.save(item2)

    all_items = passenger_repository.get_all()

    assert len(all_items) == 2
    assert 'id1' in [item['id'] for item in all_items]
    assert 'id2' in [item['id'] for item in all_items]

def test_delete_passenger(passenger_repository):
    """
    Testa se o repositório deleta um item corretamente.
    """
    passenger_id = "to-delete-456"
    item = {'id': passenger_id, 'probability': '0.9'}

    passenger_repository.save(item)
    assert passenger_repository.get_by_id(passenger_id) is not None

    passenger_repository.delete(passenger_id)

    assert passenger_repository.get_by_id(passenger_id) is None