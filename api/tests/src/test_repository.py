def test_save_and_get_passenger(passenger_repository):
    """
    Testa se o repositório salva e recupera um item corretamente.
    """
    passenger_id = "test-id-123"
    item_to_save = {
        "passenger_id": passenger_id,
        "probability": "0.75",
        "input_data": {"Age": 30},
    }

    passenger_repository.save(item_to_save)

    retrieved_item = passenger_repository.get_by_id(passenger_id)

    assert retrieved_item is not None
    assert retrieved_item["passenger_id"] == passenger_id
    assert retrieved_item["input_data"]["Age"] == 30


def test_get_all_passengers(passenger_repository):
    """
    Testa se o repositório lista todos os itens corretamente.
    """

    for i in range(12):
        passenger_repository.save({
            "passenger_id": f"test-id-{i}",
            "probability": str(i * 0.1),
            "input_data": {"Age": i + 20},
        })
    

    all_items = passenger_repository.get_all()

    assert len(all_items.get("items", [])) == 10


def test_delete_passenger(passenger_repository):
    """
    Testa se o repositório deleta um item corretamente.
    """
    passenger_id = "to-delete-456"
    item = {"passenger_id": passenger_id, "probability": "0.9"}

    passenger_repository.save(item)
    assert passenger_repository.get_by_id(passenger_id) is not None

    passenger_repository.delete(passenger_id)

    assert passenger_repository.get_by_id(passenger_id) is None
