
def parse_signals(results, keywords, signal_type):
    alerts = []
    for result in results:
        for keyword in keywords:
            if keyword.lower() in result['title'].lower():
                result['signal_type'] = signal_type
                alerts.append(result)
                break
    return alerts
