import { fetchMarketVenues, fetchPairs } from "../api-client"
import State from "../models/state"

export default async function updateForm(
  pair: string | null,
  marketvenue: string | null,
  state: State,
  setState: React.Dispatch<React.SetStateAction<State>>
) {
  if (pair && marketvenue) {
    setState({
      pair: pair,
      marketvenue: marketvenue,
      marketvenues: await fetchMarketVenues(pair),
      pairs: await fetchPairs(marketvenue),
      dataPointIndex: null
    })
  } else if (pair) {
    setState({
      pair: pair,
      marketvenue: state.marketvenue,
      marketvenues: await fetchMarketVenues(pair),
      pairs: state.pairs,
      dataPointIndex: null
    })
  } else if (marketvenue) {
    setState({
      pair: state.pair,
      marketvenue: marketvenue,
      marketvenues: state.marketvenues,
      pairs: await fetchPairs(marketvenue),
      dataPointIndex: null
    })
  } else {
    return
  }
}
