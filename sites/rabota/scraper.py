from abstract.scraper import BaseScraper
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python job listings from Robota.ua via GraphQL."""

    SITE_NAME = 'RobotaUA'
    URL = 'https://dracula.robota.ua/?q=getPublishedVacanciesList'
    GRAPHQL_QUERY = """
        query getPublishedVacanciesList(
            $filter: PublishedVacanciesFilterInput!,
            $pagination: PublishedVacanciesPaginationInput!,
            $sort: PublishedVacanciesSortType!,
            # $isBrowser: Boolean!
        ) {
            publishedVacancies(filter: $filter, pagination: $pagination, sort: $sort) {
                totalCount
                items {
                    id
                    title
                    description
                    sortDate
                    isActive
                    salary { amountFrom amountTo }
                    company { id name }
                    city { id name }
                }
            }
        }
    """
    PAYLOAD = {
        'query': GRAPHQL_QUERY,
        'variables': {
            'pagination': {'count': 50, 'page': 0},
            'filter': {
                'keywords': 'python',
                'metroBranches': [],
                'additionalKeywords': '',
                'clusterKeywords': [],
                'location': {'longitude': 0, 'latitude': 0},
                'salary': 0,
                'scheduleIds': ['1', '2', '8', '3'],
                'rubrics': [],
                'showAgencies': True,
                'showWithoutSalary': True,
                'showMilitary': True,
                'branchIds': ['2'],
            },
            'sort': 'BY_BUSINESS_SCORE',
            # 'isBrowser': False,
        },
    }

    def _request(self) -> ResponseDTO:
        """Send a GraphQL POST request to the Robota.ua API."""
        return self._client.fetch(self.URL, method='POST', json=self.PAYLOAD)
