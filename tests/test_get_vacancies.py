import requests
import allure
import pytest
from config.settings import Config


@allure.suite("API вакансий")
@allure.sub_suite("GET /vacancies")
class TestGetVacancies:

    @allure.feature("Поиск вакансий")
    @allure.story("Успешный запрос")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Успешный поиск по вакансиям — статус 200")
    def test_get_vacancies_status_code(self):
        with allure.step("Отправка GET-запроса на endpoint вакансий"):
            response = requests.get(Config.vacancies_url)
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200

    @allure.feature("Поиск вакансий")
    @allure.story("Структура ответа")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Проверка структуры JSON-ответа")
    def test_get_vacancies_response_structure(self):
        response = requests.get(Config.vacancies_url)
        response_json = response.json()
        allure.attach(str(response_json), name="Response Body", attachment_type=allure.attachment_type.JSON)
        assert isinstance(response_json.get("items"), list)
        assert "id" in response_json["items"][0]
        assert "name" in response_json["items"][0]
        assert "found" in response_json

    @allure.feature("Кластеры вакансий")
    @allure.story("Получение данных по кластерам")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Получение данных по кластерам при включённом параметре")
    def test_get_vacancies_cluster(self):
        params = {"clusters": "true"}
        response = requests.get(Config.vacancies_url, params=params)
        response_json = response.json()
        allure.attach(str(response_json.get("clusters")), name="Clusters", attachment_type=allure.attachment_type.JSON)
        assert "clusters" in response_json
        assert response_json["clusters"] is not None

    @allure.feature("Кластеры вакансий")
    @allure.story("Наличие ожидаемых кластеров")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Проверка наличия кластера: {expected_clusters}")
    @pytest.mark.parametrize("expected_clusters", [
        "Регион", "Уровень дохода", "Отрасль компании", "Опыт работы",
        "Тип занятости", "График работы", "Исключение", "Профессиональная роль",
        "Образование", "оформление по ГПХ или по совместительству"
    ])
    def test_expected_clusters_present(self, expected_clusters):
        params = {"clusters": "true"}
        response = requests.get(Config.vacancies_url, params=params)
        clusters = response.json().get("clusters", [])
        cluster_names = [cluster.get("name") for cluster in clusters]
        allure.attach(str(cluster_names), name="Cluster names", attachment_type=allure.attachment_type.TEXT)
        assert expected_clusters in cluster_names

    @allure.feature("Фильтрация вакансий")
    @allure.story("По региону")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Фильтрация по региону: Москва")
    def test_filter_by_area(self):
        params = {"area": 1}
        response = requests.get(Config.vacancies_url, params=params)
        response_json = response.json()
        assert response.status_code == 200
        for item in response_json["items"]:
            assert "Москва" in item["area"]["name"]

    @allure.feature("Фильтрация вакансий")
    @allure.story("По названию вакансии")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Фильтрация по названию вакансии: QA")
    def test_filter_by_name(self):
        params = {"per_page": 10, "search_field": "name", "text": "QA"}
        response = requests.get(Config.vacancies_url, params=params)
        response_json = response.json()
        assert len(response_json["items"]) == 10
        for vacancy in response_json["items"]:
            assert "QA" in vacancy["name"]

    @allure.feature("Ошибки валидации")
    @allure.story("Некорректный параметр per_page")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Ошибка при передаче per_page=101")
    def test_invalid_page_number(self):
        params = {"per_page": 101}
        response = requests.get(Config.vacancies_url, params=params)
        response_json = response.json()
        assert response.status_code == 400
        assert "errors" in response_json
        error = response_json["errors"][0]
        with allure.step("Проверка значения ошибки"):
            assert error.get("value") == "per_page"
            assert error.get("type") == "bad_argument"

    @allure.feature("Ограничение количества результатов")
    @allure.story("Проверка per_page=1")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Проверка, что per_page=1 возвращает 1 вакансию")
    def test_per_page_limit(self):
        params = {"per_page": 1}
        response = requests.get(Config.vacancies_url, params=params)
        response_json = response.json()
        allure.attach(response.text, name="Response", attachment_type=allure.attachment_type.JSON)
        assert len(response_json["items"]) == 1
