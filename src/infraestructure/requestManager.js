class RequestManager {
  static #instance = null;

  #baseURL = "";
  #defaultHeaders = {};
  #activeRequests = new Map();
  #requestQueue = [];
  #maxConcurrent = 5;
  #running = 0;

  constructor(config = {}) {
    if (RequestManager.#instance) {
      throw new Error(
        "A instância do RequestManager já foi criada."
      );
    }

    this.#baseURL = config.baseURL ?? "";
    this.#defaultHeaders = {
      "Content-Type": "application/json",
      ...config.headers,
    };
    this.#maxConcurrent = config.maxConcurrent ?? 5;

    console.log("[RequestManager] Instância criada.");
  }
  static getInstance(config = {}) {
    if (!RequestManager.#instance) {
      RequestManager.#instance = new RequestManager(config);
    }
    return RequestManager.#instance;
  }
  setBaseURL(url) {
    this.#baseURL = url;
    return this;
  }

  setDefaultHeader(key, value) {
    this.#defaultHeaders[key] = value;
    return this;
  }

  setAuthToken(token) {
    this.#defaultHeaders["Authorization"] = `Bearer ${token}`;
    return this;
  }

  // Requisição principal do RequestManager
  async request(endpoint, options = {}) {
    const url = `${this.#baseURL}${endpoint}`;
    const requestId = `${options.method ?? "GET"}:${url}:${Date.now()}`;

    const mergedOptions = {
      method: "GET",
      ...options,
      headers: {
        ...this.#defaultHeaders,
        ...options.headers,
      },
    };

    return this.#enqueue(requestId, url, mergedOptions);
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  }

  post(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  put(endpoint, body, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body),
    });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  }

  #enqueue(id, url, options) {
    return new Promise((resolve, reject) => {
      this.#requestQueue.push({ id, url, options, resolve, reject });
      this.#processQueue();
    });
  }

  #processQueue() {
    while (this.#running < this.#maxConcurrent && this.#requestQueue.length) {
      const task = this.#requestQueue.shift();
      this.#running++;
      this.#execute(task).finally(() => {
        this.#running--;
        this.#processQueue();
      });
    }
  }

  async #execute({ id, url, options, resolve, reject }) {
    const controller = new AbortController();
    this.#activeRequests.set(id, controller);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      resolve(data);
    } catch (error) {
      reject(error);
    } finally {
      this.#activeRequests.delete(id);
    }
  }

  cancelAll() {
    this.#activeRequests.forEach((controller) => controller.abort());
    this.#activeRequests.clear();
    this.#requestQueue = [];
    this.#running = 0;
    console.log("[RequestManager] Todas as requisições foram canceladas.");
  }

  getStats() {
    return {
      active: this.#activeRequests.size,
      queued: this.#requestQueue.length,
      running: this.#running,
      maxConcurrent: this.#maxConcurrent,
    };
  }

  static _resetInstance() {
    RequestManager.#instance = null;
  }
}

module.exports = { RequestManager };
