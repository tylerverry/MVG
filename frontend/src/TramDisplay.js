const root = document.getElementById('root');

function TramDisplay() {
  const [data, setData] = React.useState(null);
  const [error, setError] = React.useState(null);
  const WALKING_TIME = 6;

  const fetchData = async () => {
    try {
      const response = await fetch('/api/trams');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError('Failed to fetch tram data');
    }
  };

  React.useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getTimeStyle = (minutes) => {
    if (minutes < 5) return { color: '#ef4444' };
    if (minutes >= WALKING_TIME && minutes <= 8) return { color: '#22c55e' };
    return { color: '#3b82f6' };
  };

  if (error) return <div style={{color: 'red'}}>{error}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div style={{maxWidth: '48rem', margin: '0 auto', padding: '1rem'}}>
      <header style={{marginBottom: '2rem'}}>
        <h1 style={{fontSize: '1.5rem', fontWeight: 'bold'}}>Prinz-Eugen-Park Trams</h1>
        <div>{new Date().toLocaleTimeString('de-DE')}</div>
      </header>

      <div style={{marginBottom: '2rem'}}>
        <h2 style={{fontSize: '1.25rem', marginBottom: '1rem'}}>To St. Emmeram</h2>
        {data.northbound?.map((tram, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '1rem',
            marginBottom: '0.5rem',
            backgroundColor: '#f9fafb',
            borderRadius: '0.5rem'
          }}>
            <div style={{fontSize: '1.25rem'}}>Line {tram.line}</div>
            <div style={{...getTimeStyle(tram.minutes), fontSize: '1.5rem', fontWeight: 'bold'}}>
              {tram.minutes}'
            </div>
          </div>
        ))}
      </div>

      <div style={{marginBottom: '2rem'}}>
        <h2 style={{fontSize: '1.25rem', marginBottom: '1rem'}}>To Amalienburgstraße</h2>
        {data.southbound?.map((tram, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '1rem',
            marginBottom: '0.5rem',
            backgroundColor: '#f9fafb',
            borderRadius: '0.5rem'
          }}>
            <div style={{fontSize: '1.25rem'}}>Line {tram.line}</div>
            <div style={{...getTimeStyle(tram.minutes), fontSize: '1.5rem', fontWeight: 'bold'}}>
              {tram.minutes}'
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

ReactDOM.render(React.createElement(TramDisplay), root);