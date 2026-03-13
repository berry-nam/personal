import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[50vh] flex-col items-center justify-center px-4 text-center">
          <div className="rounded-2xl border border-gray-200 bg-white px-8 py-10 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900">
              문제가 발생했습니다
            </h2>
            <p className="mt-2 text-sm text-gray-500">
              페이지를 표시하는 중 오류가 발생했습니다.
            </p>
            {this.state.error && (
              <p className="mt-3 max-w-md text-xs text-gray-400">
                {this.state.error.message}
              </p>
            )}
            <button
              onClick={this.handleRetry}
              className="mt-6 rounded-lg bg-gray-900 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-gray-800"
            >
              다시 시도
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
