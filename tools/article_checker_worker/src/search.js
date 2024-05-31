export async function webSearch(params, BRAVE_API_KEY, SEARCH_ENDPOINT) {
  const apiKey = BRAVE_API_KEY;
  const url = new URL(SEARCH_ENDPOINT);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  const headers = {
      "Accept": "application/json",
      "Accept-Encoding": "gzip",
      "X-Subscription-Token": apiKey
  };
  try {
      const response = await fetch(url, { headers });

      if (response.ok) { 
          return await response.json(); 
      } else {
          return { error: true, statusCode: response.status, message: `Failed to fetch: ${response.statusText}` };
      }
  } catch (error) {
      console.error('There was a problem with the Brave Web Search API call:', error);
      return { error: true, message: error.message }; 
  }
}

export function formatResultsFull(rawSearchResults) {
let result = '<search_results>\n';
rawSearchResults.forEach((rawSearchResult, index) => {
  result += `<item index="${index + 1}">\n`;
  result += `<page_content>\n`;
  result += `Web Page Title: ${rawSearchResult.title}\n`;
  result += `Web Page URL: ${rawSearchResult.url}\n`;
  result += `Web Page Summary: <summary>`;
  result += `- ${rawSearchResult.description.replace(/<strong>/g, '').replace(/<\/strong>/g, '')}\n`;
  result += `</summary>\n`;
  result += `</page_content>\n`;
  result += `</item>\n`;
});
result += '</search_results>';
return result;
}