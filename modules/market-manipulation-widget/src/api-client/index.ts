/* eslint-disable no-var */
import axios, { AxiosError, AxiosResponse } from "axios"
import {
  DictionaryRequest,
  DictionaryResponse,
  MetricsRequest,
  MetricsResponse,
  ApiError
} from "./models"

declare var RAPID_KEY: string | undefined
declare var RAPID_HOST: string | undefined

axios.defaults.baseURL = `https://${RAPID_HOST}`

axios.interceptors.request.use((config) => {
  config.headers.set("X-RapidAPI-Key", RAPID_KEY)
  config.headers.set("X-RapidAPI-Host", RAPID_HOST)
  return config
})

axios.interceptors.response.use(
  (res) => res,
  (error: AxiosError) => {
    const { data, status } = error.response!
    switch (status) {
      case 400:
        console.error(data)
        break

      case 500:
        console.error("server-error")
        break
    }
    return Promise.reject(error)
  }
)

const responseBody = <T>(response: AxiosResponse<T>) => response.data

const get = <T>(url: string, body: object) =>
  axios.get<T>(url, { params: body }).then(responseBody)

const dictionary = (request: DictionaryRequest) =>
  get<DictionaryResponse[]>("/dictionary", request)
const metrics = (request: MetricsRequest) =>
  get<MetricsResponse[] | ApiError>("/metrics", request)

const fetchMarketVenues = async (pair: string): Promise<string[]> => {
  const response = await dictionary({
    pairid: pair,
    limit: 1000
  })

  return response.map((x) => x.marketvenueid)
}

const fetchPairs = async (marketvenueid: string): Promise<string[]> => {
  const response = await dictionary({
    marketvenueid: marketvenueid,
    limit: 1000
  })

  return response.map((x) => x.pairid)
}

export {
  dictionary,
  metrics,
  fetchMarketVenues,
  fetchPairs,
  DictionaryRequest,
  DictionaryResponse,
  MetricsRequest,
  MetricsResponse,
  ApiError
}
