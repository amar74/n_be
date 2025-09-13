/// <reference types="@types/google.maps" />
import { useEffect, useRef, useState } from 'react';
import { Input } from './input';
import { MapPin } from 'lucide-react';

declare global {
  interface Window {
    google: typeof google;
    initGooglePlaces?: () => void;
    gm_authFailure?: () => void;
  }
}

interface PlacesAutocompleteProps {
  value: string;
  onChange: (value: string, placeDetails?: google.maps.places.PlaceResult) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function PlacesAutocomplete({
  value,
  onChange,
  placeholder = 'Enter an address',
  className = '',
  disabled = false,
}: PlacesAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initializePlaces = () => {
    if (!inputRef.current || !window.google?.maps?.places) {
      setError('Places API not available');
      return;
    }

    try {
      autocompleteRef.current = new window.google.maps.places.Autocomplete(inputRef.current, {
        types: ['address'],
        fields: ['address_components', 'formatted_address', 'geometry'],
      });

      const listener = autocompleteRef.current.addListener('place_changed', () => {
        const place = autocompleteRef.current?.getPlace();
        if (!place) return;
        onChange(place.formatted_address || '', place);
      });

      setIsInitialized(true);
      setError(null);

      return () => {
        if (listener) window.google.maps.event.removeListener(listener);
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(`Failed to initialize Places Autocomplete: ${errorMessage}`);
    }
  };

  useEffect(() => {
    const handleScriptError = (event: Event | string) => {
      if (window.google?.maps?.places === undefined && window.google?.maps) {
        const error = (window as any).google.maps.errors?.[0];
        if (error?.includes('RefererNotAllowedMapError')) {
          setError(`This URL (${window.location.origin}) is not authorized. Add "${window.location.origin}/*" to allowed referrers.`);
          return;
        }
        if (error?.includes('ApiTargetBlockedMapError')) {
          setError('The Places API is not enabled for this API key.');
          return;
        }
      }
    };

    window.gm_authFailure = () => {
      setError(`Authorization failed. Please ensure "${window.location.origin}/*" is added to allowed referrers.`);
    };

    window.initGooglePlaces = () => {
      setIsLoaded(true);
      initializePlaces();
    };

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
    if (!apiKey) {
      setError('Google Maps API key is missing');
      return;
    }

    if (!document.querySelector('#google-maps-script')) {
      const script = document.createElement('script');
      script.id = 'google-maps-script';
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initGooglePlaces&v=weekly`;
      script.async = true;
      script.defer = true;
      script.onerror = handleScriptError;
      document.head.appendChild(script);
    } else if (window.google) {
      setIsLoaded(true);
      initializePlaces();
    }

    return () => {
      delete window.initGooglePlaces;
    };
  }, []);

  return (
    <div className="relative">
      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
      <Input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={error ? 'Google Maps not available' : placeholder}
        className={`pl-10 border placeholder-shown:border-gray-300 focus:border-orange-300 not-placeholder-shown:border-orange-300 focus:outline-none focus:ring-0 focus-visible:ring-0 ${
          error ? 'border-red-300 bg-red-50' : ''
        } ${className}`}
        disabled={disabled || !isLoaded || !isInitialized || !!error}
      />
      {error && (
        <div className="mt-2 p-2 text-sm bg-red-50 border border-red-200 rounded-md">
          <div className="font-medium text-red-800">Error loading Google Maps</div>
          <div className="mt-1 text-red-600">{error}</div>
          {error.includes('not authorized') && (
            <div className="mt-2 text-red-700">
              <ol className="mt-1 ml-4 list-decimal">
                <li>Go to Google Cloud Console</li>
                <li>Navigate to "APIs & Services" {'->'} "Credentials"</li>
                <li>Edit your API key</li>
                <li>Add these URLs:
                  <pre className="mt-1 p-2 bg-red-100 rounded text-xs font-mono">
                    {`http://localhost:5173/*\nhttp://localhost:5173`}
                  </pre>
                </li>
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
}