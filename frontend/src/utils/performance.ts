/**
 * 前端性能优化工具函数
 */

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(func: T, limit: number): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return function (this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(func: T, delay: number): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return function (this: any, ...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

/**
 * 代码分割 - 动态导入组件
 */
export async function lazyLoadComponent<T>(importFunc: () => Promise<{ default: T }>): Promise<T> {
  const module = await importFunc();
  return module.default;
}

/**
 * 图片懒加载
 */
export function lazyLoadImage(imgElement: HTMLImageElement) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        const src = img.dataset.src;
        if (src) {
          img.src = src;
          img.removeAttribute("data-src");
        }
        observer.unobserve(img);
      }
    });
  });

  observer.observe(imgElement);
}

/**
 * 请求缓存
 */
class RequestCache {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private ttl: number;

  constructor(ttl: number = 5 * 60 * 1000) {
    this.ttl = ttl;
  }

  get(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const isExpired = Date.now() - cached.timestamp > this.ttl;
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  set(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  clear(): void {
    this.cache.clear();
  }
}

export const apiCache = new RequestCache();

/**
 * 批量请求合并
 */
export class RequestBatcher<T, R> {
  private queue: Array<{ key: T; resolve: (value: R) => void; reject: (error: any) => void }> = [];
  private batchFn: (keys: T[]) => Promise<R[]>;
  private delay: number;
  private timeoutId: ReturnType<typeof setTimeout> | null = null;

  constructor(batchFn: (keys: T[]) => Promise<R[]>, delay: number = 50) {
    this.batchFn = batchFn;
    this.delay = delay;
  }

  add(key: T): Promise<R> {
    return new Promise((resolve, reject) => {
      this.queue.push({ key, resolve, reject });

      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }

      this.timeoutId = setTimeout(() => this.flush(), this.delay);
    });
  }

  private async flush(): Promise<void> {
    if (this.queue.length === 0) return;

    const batch = this.queue.splice(0, this.queue.length);
    const keys = batch.map((item) => item.key);

    try {
      const results = await this.batchFn(keys);
      batch.forEach((item, index) => {
        item.resolve(results[index]);
      });
    } catch (error) {
      batch.forEach((item) => {
        item.reject(error);
      });
    }
  }
}

/**
 * 性能监控
 */
export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();

  measure(name: string, fn: () => void): void {
    const start = performance.now();
    fn();
    const duration = performance.now() - start;

    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(duration);
  }

  async measureAsync(name: string, fn: () => Promise<void>): Promise<void> {
    const start = performance.now();
    await fn();
    const duration = performance.now() - start;

    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(duration);
  }

  getStats(name: string): { avg: number; min: number; max: number; count: number } | null {
    const values = this.metrics.get(name);
    if (!values || values.length === 0) return null;

    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);

    return { avg, min, max, count: values.length };
  }

  clear(): void {
    this.metrics.clear();
  }

  report(): void {
    console.group("Performance Report");
    this.metrics.forEach((_, name) => {
      const stats = this.getStats(name);
      if (stats) {
        console.log(`${name}:`, {
          avg: `${stats.avg.toFixed(2)}ms`,
          min: `${stats.min.toFixed(2)}ms`,
          max: `${stats.max.toFixed(2)}ms`,
          count: stats.count,
        });
      }
    });
    console.groupEnd();
  }
}

export const performanceMonitor = new PerformanceMonitor();
