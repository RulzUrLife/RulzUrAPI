import abc

next_id = lambda l: l[-1]['id'] + 1


class TestEndpoint(abc.ABC):

    @staticmethod
    def _test_incorrect_json(method, endpoint):
        incorrect_json = '{'
        data_expected = {
            'status_code': 400,
            'message': 'request malformed',
            'errors': 'JSON is incorrect'
        }

        res = method(endpoint)
        assert res.status_code == 400
        assert res.data == data_expected

        res = method(endpoint, data=incorrect_json)
        assert res.status_code == 400
        assert res.data == data_expected

    @abc.abstractmethod
    def test_list(self, client, data_expected):
        res = client.get(self.endpoint)

        assert res.status_code == 200
        assert res.data == data_expected

    @abc.abstractmethod
    def test_post(self, client, data, data_expected):
        res = client.post(self.endpoint, data=data)

        assert res.status_code == 201
        assert res.data == data_expected

    def test_post_incorrect_json(self, client):
        self._test_incorrect_json(client.post, self.endpoint)

    @abc.abstractmethod
    def test_post_invalid(self, client, data_list):
        for data, errors in data_list:
            res = client.post(self.endpoint, data=data)

            assert res.status_code == 400
            assert res.data['status_code'] == 400
            assert res.data['message'] == 'request malformed'
            assert res.data['errors'] == errors

    @abc.abstractmethod
    def test_post_409(self, client, data, error):
        res = client.post(self.endpoint, data=data)

        assert res.status_code == 409
        assert res.data['message'] == error

    @abc.abstractmethod
    def test_put_list(self, client, data, data_expected):
        res = client.put(self.endpoint, data=data)

        assert res.status_code == 200
        assert res.data == data_expected

    @abc.abstractmethod
    def test_get(self, client, data_id, data_expected):
        res = client.get('%s/%d' % (self.endpoint, data_id))

        assert res.status_code == 200
        assert res.data == data_expected

    @abc.abstractmethod
    def test_get_404(self, client, data_id, error_msg):
        res = client.get('%s/%d' % (self.endpoint, data_id))

        assert res.status_code == 404
        assert res.data['message'] == error_msg

    @abc.abstractmethod
    def test_put(self, client, data, data_expected):
        res = client.put('%s/%d' % (self.endpoint, data['id']), data=data)
        assert res.status_code == 200
        assert res.data == data_expected

    def test_put_incorrect_json(self, client):
        endpoint = '%s/%d' % (self.endpoint, int())
        self._test_incorrect_json(client.put, endpoint)


    def test_put_empty_data(self, client):
        res = client.put('%s/%d' % (self.endpoint, int()), data={'foo': 'bar'})

        assert res.status_code == 400
        assert res.data == {
            'status_code': 400,
            'message': 'no data provided for update'
        }

    @abc.abstractmethod
    def test_put_404(self, client, data, error_msg):
        res = client.put('%s/%d' % (self.endpoint, data['id']), data=data)

        assert res.status_code == 404
        assert res.data['message'] == error_msg
