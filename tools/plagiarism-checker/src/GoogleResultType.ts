// from https://github.com/googleapis/google-api-nodejs-client/blob/main/src/apis/customsearch/v1.ts#L164
export interface SearchResult {
  cacheId?: string | null
  displayLink?: string | null
  fileFormat?: string | null
  formattedUrl?: string | null
  htmlFormattedUrl?: string | null
  htmlSnippet?: string | null
  htmlTitle?: string | null
  image?: {
    byteSize?: number
    contextLink?: string
    height?: number
    thumbnailHeight?: number
    thumbnailLink?: string
    thumbnailWidth?: number
    width?: number
  } | null
  kind?: string | null
  labels?: Array<{
    displayName?: string
    label_with_op?: string
    name?: string
  }> | null
  link?: string | null
  mime?: string | null
  pagemap?: { [key: string]: any } | null
  snippet?: string | null
  title?: string | null
}

export interface Schema$Promotion {
  bodyLines?: Array<{
    htmlTitle?: string
    link?: string
    title?: string
    url?: string
  }> | null
  displayLink?: string | null
  htmlTitle?: string | null
  image?: { height?: number; source?: string; width?: number } | null
  link?: string | null
  title?: string | null
}

export interface SearchResponse {
  context?: { [key: string]: any } | null
  items?: SearchResult[]
  kind?: string | null
  promotions?: Schema$Promotion[]
  queries?: {
    nextPage?: Array<{
      count?: number
      cr?: string
      cx?: string
      dateRestrict?: string
      disableCnTwTranslation?: string
      exactTerms?: string
      excludeTerms?: string
      fileType?: string
      filter?: string
      gl?: string
      googleHost?: string
      highRange?: string
      hl?: string
      hq?: string
      imgColorType?: string
      imgDominantColor?: string
      imgSize?: string
      imgType?: string
      inputEncoding?: string
      language?: string
      linkSite?: string
      lowRange?: string
      orTerms?: string
      outputEncoding?: string
      relatedSite?: string
      rights?: string
      safe?: string
      searchTerms?: string
      searchType?: string
      siteSearch?: string
      siteSearchFilter?: string
      sort?: string
      startIndex?: number
      startPage?: number
      title?: string
      totalResults?: string
    }>
    previousPage?: Array<{
      count?: number
      cr?: string
      cx?: string
      dateRestrict?: string
      disableCnTwTranslation?: string
      exactTerms?: string
      excludeTerms?: string
      fileType?: string
      filter?: string
      gl?: string
      googleHost?: string
      highRange?: string
      hl?: string
      hq?: string
      imgColorType?: string
      imgDominantColor?: string
      imgSize?: string
      imgType?: string
      inputEncoding?: string
      language?: string
      linkSite?: string
      lowRange?: string
      orTerms?: string
      outputEncoding?: string
      relatedSite?: string
      rights?: string
      safe?: string
      searchTerms?: string
      searchType?: string
      siteSearch?: string
      siteSearchFilter?: string
      sort?: string
      startIndex?: number
      startPage?: number
      title?: string
      totalResults?: string
    }>
    request?: Array<{
      count?: number
      cr?: string
      cx?: string
      dateRestrict?: string
      disableCnTwTranslation?: string
      exactTerms?: string
      excludeTerms?: string
      fileType?: string
      filter?: string
      gl?: string
      googleHost?: string
      highRange?: string
      hl?: string
      hq?: string
      imgColorType?: string
      imgDominantColor?: string
      imgSize?: string
      imgType?: string
      inputEncoding?: string
      language?: string
      linkSite?: string
      lowRange?: string
      orTerms?: string
      outputEncoding?: string
      relatedSite?: string
      rights?: string
      safe?: string
      searchTerms?: string
      searchType?: string
      siteSearch?: string
      siteSearchFilter?: string
      sort?: string
      startIndex?: number
      startPage?: number
      title?: string
      totalResults?: string
    }>
  } | null
  searchInformation?: {
    formattedSearchTime?: string
    formattedTotalResults?: string
    searchTime?: number
    totalResults?: string
  } | null
  spelling?: { correctedQuery?: string; htmlCorrectedQuery?: string } | null
  url?: { template?: string; type?: string } | null
}
