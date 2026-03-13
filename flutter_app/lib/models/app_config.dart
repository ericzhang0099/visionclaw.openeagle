class AppConfig {
  final String baseUrl;
  final String wsUrl;
  final int timeout;
  final bool debug;

  AppConfig({
    required this.baseUrl,
    required this.wsUrl,
    this.timeout = 30000,
    this.debug = false,
  });

  factory AppConfig.defaultConfig() {
    return AppConfig(
      baseUrl: 'http://172.24.171.60:8000',
      wsUrl: 'ws://172.24.171.60:8000',
      timeout: 30000,
      debug: true,
    );
  }

  factory AppConfig.fromJson(Map<String, dynamic> json) {
    return AppConfig(
      baseUrl: json['baseUrl'] ?? 'http://172.24.171.60:8000',
      wsUrl: json['wsUrl'] ?? 'ws://172.24.171.60:8000',
      timeout: json['timeout'] ?? 30000,
      debug: json['debug'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'baseUrl': baseUrl,
      'wsUrl': wsUrl,
      'timeout': timeout,
      'debug': debug,
    };
  }

  AppConfig copyWith({
    String? baseUrl,
    String? wsUrl,
    int? timeout,
    bool? debug,
  }) {
    return AppConfig(
      baseUrl: baseUrl ?? this.baseUrl,
      wsUrl: wsUrl ?? this.wsUrl,
      timeout: timeout ?? this.timeout,
      debug: debug ?? this.debug,
    );
  }
}
