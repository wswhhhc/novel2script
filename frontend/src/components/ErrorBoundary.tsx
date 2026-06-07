import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  /** 可选的自定义 fallback UI。不传时使用默认的全页错误界面。 */
  fallback?: (error: Error | null, reset: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * 错误边界，捕获子组件树中的渲染异常。
 *
 * - 顶层使用（无 fallback）：显示全页错误界面 + 刷新/恢复按钮
 * - 局部使用（传 fallback）：显示区域级错误卡片，不波及整体布局
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleReset);
      }

      return (
        <div className="error-boundary-fallback">
          <div className="error-boundary-card">
            <h2>页面出错了</h2>
            <p>组件渲染时发生异常，请尝试刷新页面。</p>
            {this.state.error && (
              <details>
                <summary>错误详情</summary>
                <pre>{this.state.error.message}</pre>
              </details>
            )}
            <div className="error-boundary-actions">
              <button type="button" className="primary-button" onClick={() => window.location.reload()}>
                刷新页面
              </button>
              <button type="button" className="primary-button" onClick={this.handleReset}>
                尝试恢复
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
