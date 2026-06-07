import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock global fetch before importing client
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

interface MockResponseInit {
  ok?: boolean;
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
  body?: string | object;
}

function mockResponse(init: MockResponseInit) {
  const { ok = true, status = 200, statusText = "OK", headers = {}, body = "" } = init;
  const bodyString = typeof body === "object" ? JSON.stringify(body) : body;
  return new Response(bodyString, {
    status,
    statusText,
    headers: { "content-type": "application/json", ...headers },
  });
}

describe("API Client", () => {
  let client: typeof import("../client");

  beforeEach(() => {
    vi.clearAllMocks();
    // Re-import with fresh mocks
    return import("../client").then((m) => {
      client = m;
    });
  });

  describe("request (generic fetch wrapper)", () => {
    it("sends fetch request to correct URL", async () => {
      mockFetch.mockResolvedValueOnce(mockResponse({ body: { status: "ok" } }));

      const result = await client.checkHealth();

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain("/health");
      expect(options.headers).toHaveProperty("Content-Type", "application/json");
      expect(result).toEqual({ status: "ok" });
    });

    it("extracts error from string body", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response("Service unavailable", {
          status: 503,
          statusText: "Service Unavailable",
          headers: { "content-type": "text/plain" },
        })
      );

      await expect(client.checkHealth()).rejects.toThrow("Service unavailable");
    });

    it("extracts error from JSON detail field", async () => {
      mockFetch.mockResolvedValueOnce(
        mockResponse({
          ok: false,
          status: 422,
          body: { detail: "Validation error occurred" },
        })
      );

      await expect(client.checkHealth()).rejects.toThrow("Validation error occurred");
    });

    it("extracts error from array of validation errors", async () => {
      mockFetch.mockResolvedValueOnce(
        mockResponse({
          ok: false,
          status: 422,
          body: {
            detail: [
              { loc: ["body", "title"], msg: "Field required", type: "missing" },
              { loc: ["body", "content"], msg: "String should not be empty", type: "string" },
            ],
          },
        })
      );

      await expect(client.checkHealth()).rejects.toThrow("Field required；String should not be empty");
    });

    it("falls back to statusText when no detail field", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response("", {
          status: 500,
          statusText: "Internal Server Error",
          headers: { "content-type": "text/plain" },
        })
      );

      await expect(client.checkHealth()).rejects.toThrow("Internal Server Error");
    });
  });

  describe("parseChapters", () => {
    it("sends post with content body", async () => {
      mockFetch.mockResolvedValueOnce(
        mockResponse({
          body: { chapter_count: 3, valid: true, message: "OK", warnings: [], chapters: [] },
        })
      );

      const result = await client.parseChapters("test content");

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain("/api/chapters/parse");
      expect(options.method).toBe("POST");
      expect(JSON.parse(options.body)).toEqual({ content: "test content" });
      expect(result.chapter_count).toBe(3);
    });
  });

  describe("validateYaml", () => {
    it("sends post with yaml body", async () => {
      mockFetch.mockResolvedValueOnce(mockResponse({ body: { valid: true, errors: [] } }));

      const result = await client.validateYaml("test: yaml");

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe("POST");
      expect(JSON.parse(options.body)).toEqual({ yaml: "test: yaml" });
      expect(result.valid).toBe(true);
    });
  });

  describe("generateScript (non-streaming)", () => {
    it("sends post with title, genre, chapters", async () => {
      const chapters = [{ id: "C001", title: "Ch1", content: "test", word_count: 100 }];
      mockFetch.mockResolvedValueOnce(
        mockResponse({ body: { yaml: "output", validation: { valid: true, errors: [] } } })
      );

      const result = await client.generateScript("Test", "悬疑", chapters);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain("/api/script/generate");
      expect(JSON.parse(options.body)).toEqual({ title: "Test", genre: "悬疑", chapters });
      expect(result.yaml).toBe("output");
    });
  });

  describe("listProjects", () => {
    it("returns project array", async () => {
      const projects = [
        {
          id: 1,
          title: "P1",
          genre: "悬疑",
          chapter_count: 3,
          generation_mode: "mock",
          created_at: "",
          updated_at: "",
        },
      ];
      mockFetch.mockResolvedValueOnce(mockResponse({ body: projects }));

      const result = await client.listProjects();

      expect(result).toHaveLength(1);
      expect(result[0].title).toBe("P1");
    });
  });

  describe("createProject", () => {
    it("sends post with project payload", async () => {
      const payload = {
        title: "New",
        genre: "悬疑",
        source_content: "content",
        chapters: [],
        yaml: "",
        validation: null,
        generation_mode: "mock" as const,
      };
      mockFetch.mockResolvedValueOnce(
        mockResponse({ body: { id: 1, ...payload, chapter_count: 0, created_at: "", updated_at: "" } })
      );

      const result = await client.createProject(payload);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain("/api/projects");
      expect(options.method).toBe("POST");
      expect(result.id).toBe(1);
    });
  });

  describe("exportProject", () => {
    function mockExportResponse(headers: Record<string, string>): Response {
      // jsdom 不支持 new Response(blob)，用 text body + 模拟 blob()
      const bodyText = "test content";
      const response = new Response(bodyText, { headers });
      // 覆盖 blob() 方法返回 mock Blob
      response.blob = () => Promise.resolve(new Blob([bodyText], { type: headers["content-type"] || "text/plain" }));
      return response;
    }

    it("downloads blob with extracted filename", async () => {
      mockFetch.mockResolvedValueOnce(
        mockExportResponse({ "content-type": "text/plain", "content-disposition": 'filename="output.md"' })
      );

      const result = await client.exportProject(1, "markdown");

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url] = mockFetch.mock.calls[0];
      expect(url).toContain("/api/projects/1/export/markdown");
      expect(result.filename).toBe("output.md");
      expect(result.blob).toBeInstanceOf(Blob);
    });

    it("handles RFC 5987 encoded filenames", async () => {
      mockFetch.mockResolvedValueOnce(
        mockExportResponse({
          "content-type": "text/plain",
          "content-disposition": "attachment; filename*=UTF-8''%E4%B8%AD%E6%96%87.md",
        })
      );

      const result = await client.exportProject(1, "yaml");

      expect(result.filename).toBe("中文.md");
    });

    it("uses default filename when no content-disposition", async () => {
      mockFetch.mockResolvedValueOnce(mockExportResponse({ "content-type": "text/plain" }));

      const result = await client.exportProject(1, "json");

      expect(result.filename).toBe("novel2script_script.json");
    });
  });

  describe("generateScriptStream", () => {
    function mockStreamResponse(ndjson: string): Response {
      // jsdom 不支持 ReadableStream Response，模拟 response.body.getReader()
      const encoder = new TextEncoder();
      const bytes = encoder.encode(ndjson);
      let pos = 0;

      const reader: ReadableStreamDefaultReader<Uint8Array> = {
        read: async () => {
          if (pos >= bytes.length) return { value: undefined, done: true };
          const chunk = bytes.slice(pos, pos + bytes.length);
          pos = bytes.length;
          return { value: chunk, done: false };
        },
        cancel: async () => {},
        releaseLock: () => {},
        closed: Promise.resolve(undefined),
      } as unknown as ReadableStreamDefaultReader<Uint8Array>;

      const response = new Response(null, {
        headers: { "content-type": "application/x-ndjson" },
      });
      Object.defineProperty(response, "body", { value: { getReader: () => reader }, writable: false });
      return response;
    }

    it("parses NDJSON events", async () => {
      const ndjson = [
        JSON.stringify({ type: "status", message: "starting", progress: 10 }),
        JSON.stringify({ type: "yaml_delta", delta: "line1\n", progress: 30 }),
        JSON.stringify({ type: "validation", validation: { valid: true, errors: [] }, progress: 50 }),
        JSON.stringify({
          type: "done",
          yaml: "line1\n",
          validation: { valid: true, errors: [] },
          message: "done",
          progress: 100,
        }),
      ].join("\n");

      mockFetch.mockResolvedValueOnce(mockStreamResponse(ndjson));

      const events: Record<string, unknown>[] = [];
      const onEvent = vi.fn((e) => events.push(e));

      await client.generateScriptStream("Test", "悬疑", [], onEvent);

      expect(onEvent).toHaveBeenCalledTimes(4);
      expect(events[0]).toMatchObject({ type: "status", message: "starting" });
      expect(events[1]).toMatchObject({ type: "yaml_delta", delta: "line1\n" });
      expect(events[2]).toMatchObject({ type: "validation" });
      expect(events[3]).toMatchObject({ type: "done", progress: 100 });
    });

    it("handles partial lines across chunks", async () => {
      const event1 = JSON.stringify({ type: "status", message: "start" });
      const event2 = JSON.stringify({ type: "yaml_delta", delta: "data" });

      function chunkedStreamReader(): ReadableStreamDefaultReader<Uint8Array> {
        const encoder = new TextEncoder();
        const chunks = [
          encoder.encode(event1.slice(0, 20)),
          encoder.encode(event1.slice(20) + "\n" + event2.slice(0, 10)),
          encoder.encode(event2.slice(10) + "\n"),
        ];
        let i = 0;
        return {
          read: async () => {
            if (i >= chunks.length) return { value: undefined, done: true };
            return { value: chunks[i++], done: false };
          },
          cancel: async () => {},
          releaseLock: () => {},
          closed: Promise.resolve(undefined),
        } as unknown as ReadableStreamDefaultReader<Uint8Array>;
      }

      const response = new Response(null);
      Object.defineProperty(response, "body", {
        value: { getReader: () => chunkedStreamReader() },
        writable: false,
      });
      mockFetch.mockResolvedValueOnce(response);

      const onEvent = vi.fn();
      await client.generateScriptStream("Test", "悬疑", [], onEvent);

      expect(onEvent).toHaveBeenCalledTimes(2);
      expect(onEvent.mock.calls[0][0]).toMatchObject({ type: "status" });
      expect(onEvent.mock.calls[1][0]).toMatchObject({ type: "yaml_delta" });
    });

    it("throws on stream error event", async () => {
      // 模拟 App.tsx 中对 error 事件的处理逻辑
      const onEvent = vi.fn((event) => {
        if (event.type === "error") {
          throw new Error(event.message);
        }
      });
      const ndjson = JSON.stringify({ type: "error", message: "Generation failed" }) + "\n";
      mockFetch.mockResolvedValueOnce(mockStreamResponse(ndjson));

      await expect(client.generateScriptStream("Test", "悬疑", [], onEvent)).rejects.toThrow("Generation failed");
    });

    it("throws on non-ok response", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response("Bad Request", {
          status: 400,
          statusText: "Bad Request",
          headers: { "content-type": "text/plain" },
        })
      );

      const onEvent = vi.fn();
      await expect(client.generateScriptStream("Test", "悬疑", [], onEvent)).rejects.toThrow("Bad Request");
    });
  });

  describe("getGenerationMode", () => {
    it("returns mode configuration", async () => {
      const mode = {
        mode: "ai" as const,
        ai_enabled: true,
        provider: "openai",
        model: "deepseek-v4-flash",
        base_url_configured: true,
        api_key_configured: true,
        auto_fix_attempts: 3,
      };
      mockFetch.mockResolvedValueOnce(mockResponse({ body: mode }));

      const result = await client.getGenerationMode();

      expect(result.mode).toBe("ai");
      expect(result.provider).toBe("openai");
    });
  });

  describe("project CRUD", () => {
    it("getProject returns project detail", async () => {
      const detail = {
        id: 1,
        title: "P1",
        genre: "悬疑",
        chapter_count: 3,
        source_content: "c",
        chapters: [],
        current_yaml: "y",
        validation: { valid: true, errors: [] },
        generation_mode: "mock" as const,
        created_at: "",
        updated_at: "",
      };
      mockFetch.mockResolvedValueOnce(mockResponse({ body: detail }));

      const result = await client.getProject(1);

      expect(result.title).toBe("P1");
      expect(result.chapter_count).toBe(3);
    });

    it("updateProject sends PUT with partial payload", async () => {
      const update = { title: "Updated" };
      mockFetch.mockResolvedValueOnce(
        mockResponse({
          body: {
            id: 1,
            title: "Updated",
            genre: "都市",
            chapter_count: 0,
            source_content: "",
            chapters: [],
            current_yaml: "",
            validation: { valid: true, errors: [] },
            generation_mode: "mock" as const,
            created_at: "",
            updated_at: "",
          },
        })
      );

      const result = await client.updateProject(1, update);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe("PUT");
      expect(result.title).toBe("Updated");
    });

    it("deleteProject sends DELETE", async () => {
      mockFetch.mockResolvedValueOnce(mockResponse({ body: { message: "deleted", id: 1 } }));

      await client.deleteProject(1);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe("DELETE");
    });
  });

  describe("version management", () => {
    it("createVersion sends POST with payload", async () => {
      const payload = { version_name: "v1", yaml: "y", validation: null, note: "" };
      mockFetch.mockResolvedValueOnce(
        mockResponse({ body: { id: 1, project_id: 1, version_name: "v1", note: "", created_at: "" } })
      );

      const result = await client.createVersion(1, payload);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe("POST");
      expect(result.version_name).toBe("v1");
    });

    it("listVersions returns version array", async () => {
      mockFetch.mockResolvedValueOnce(mockResponse({ body: [] }));

      const result = await client.listVersions(1);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url] = mockFetch.mock.calls[0];
      expect(url).toContain("/api/projects/1/versions");
      expect(result).toEqual([]);
    });

    it("restoreVersion sends POST to restore endpoint", async () => {
      const detail = {
        id: 1,
        title: "P1",
        genre: "悬疑",
        chapter_count: 3,
        source_content: "",
        chapters: [],
        current_yaml: "",
        validation: { valid: true, errors: [] },
        generation_mode: "mock" as const,
        created_at: "",
        updated_at: "",
        restored_from_version: 1,
      };
      mockFetch.mockResolvedValueOnce(mockResponse({ body: detail }));

      const result = await client.restoreVersion(1, 1);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain("/api/projects/1/versions/1/restore");
      expect(options.method).toBe("POST");
      expect(result.restored_from_version).toBe(1);
    });
  });
});
