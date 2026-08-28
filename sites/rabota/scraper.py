from abstract.client import BaseClient
from abstract.scraper import BaseScraper
from clients.curl_client import CurlClient
from core.dto import ResponseDTO


class Scraper(BaseScraper):
    """Fetches Python job listings from Robota.ua via GraphQL."""

    SITE_NAME = 'RobotaUA'
    URL = 'https://dracula.robota.ua/?q=getPublishedVacanciesList'
    GRAPHQL_QUERY = """
        query getPublishedVacanciesList($filter: PublishedVacanciesFilterInput!, $pagination: PublishedVacanciesPaginationInput!, $sort: PublishedVacanciesSortType!, $isBrowser: Boolean!) {
          publishedVacancies(filter: $filter, pagination: $pagination, sort: $sort) {
            totalCount
            items {
              ...PublishedVacanciesItem
              __typename
            }
            __typename
          }
        }
        
        fragment PublishedVacanciesItem on Vacancy {
          id
          schedules {
            id
            __typename
          }
          title
          distanceText
          description
          showLogo
          sortDate
          hot
          designBannerUrl
          isPublicationInAllCities
          badges {
            name
            __typename
          }
          salary {
            amount
            comment
            amountFrom
            amountTo
            __typename
          }
          company {
            id
            logoUrl
            name
            honors {
              badge {
                iconUrl
                tooltipDescription
                locations
                isFavorite
                __typename
              }
              __typename
            }
            __typename
          }
          city {
            id
            name
            __typename
          }
          showProfile
          seekerFavorite @include(if: $isBrowser) {
            isFavorite
            __typename
          }
          seekerDisliked @include(if: $isBrowser) {
            isDisliked
            __typename
          }
          formApplyCustomUrl
          anonymous
          isActive
          publicationType
          branding {
            ...PublishedVacancyBranding
            ...PublishedVacancyBrandingByStudio
            __typename
          }
          __typename
        }
        
        fragment PublishedVacancyBranding on VacancyBranding {
          id
          name
          banner {
            media {
              ...PublishedVacancyBrandingMediaImage
              __typename
            }
            __typename
          }
          __typename
        }
        
        fragment PublishedVacancyBrandingMediaImage on MediaImage {
          fileName
          url
          __typename
        }
        
        fragment PublishedVacancyBrandingByStudio on VacancyBrandingByStudio {
          id
          name
          bannerByStudio: banner {
            media {
              ...PublishedVacancyBrandingMediaImage
              __typename
            }
            __typename
          }
          __typename
        }
    """

    PAYLOAD = {
        'query': GRAPHQL_QUERY,
        'variables': {
            "pagination": {
              "count": 20,
              "page": 1
            },
            "filter": {
                "keywords": "python",
                "metroBranches": [],
                "additionalKeywords": "",
                "clusterKeywords": [],
                "location": {
                    "longitude": 0,
                    "latitude": 0
                },
                "salary": 0,
                "districtIds": [],
                "microDistrictIds": [],
                "scheduleIds": [],
                "rubrics": [],
                "showAgencies": True,
                "showOnlyNoCvApplyVacancies": False,
                "showOnlySpecialNeeds": False,
                "showOnlyWithoutExperience": False,
                "showOnlyNotViewed": False,
                "showWithoutSalary": True,
                "showMilitary": True,
                "isReservation": False,
                "isForVeterans": False,
                "isOfficeWithGenerator": False,
                "isOfficeWithShelter": False,
                "isMilitary": False,
                "gender": None,
                "branchIds": [],
            },
            "sort": "BY_BUSINESS_SCORE",
            "isBrowser": True
        },
    }

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/148.0.0.0 Safari/537.36'
    }

    def __init__(self, proxy: str | None = None, client: BaseClient | None = None):
        super().__init__(proxy, client=client or CurlClient())

    def _request(self) -> ResponseDTO:
        """Send a GraphQL POST request to the Robota.ua API."""
        return self._client.fetch(self.URL, method='POST', json=self.PAYLOAD, headers=self.HEADERS)
