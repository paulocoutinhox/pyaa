import Cookies from "js-cookie";
import {Configuration} from "./api-client";


export function getApiConfiguration(serverBaseUrl) {
  return new Configuration({
    basePath: serverBaseUrl,
    headers: getApiHeaders(),
  });
}

export function getApiHeaders() {
  return {
    'X-CSRFToken': Cookies.get('csrftoken'),
  }
}
