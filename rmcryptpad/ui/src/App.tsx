import {
  buildCardDetails,
  buildLoginUrl,
  type CryptPadCardData,
  type CryptPadCardMeta,
} from "@/lib/metadata";
import cryptpadMarkUrl from "./assets/cryptpad-mark.svg";

import "./index.css";

export interface AppProps {
  data: CryptPadCardData;
  meta: CryptPadCardMeta;
}

export default function App({ data, meta }: AppProps) {
  const card = buildCardDetails(meta);
  const loginUrl = buildLoginUrl(data.url);

  return (
    <main className={`cryptpad-shell theme-${card.theme}`} data-theme={card.theme}>
      <section className="cryptpad-card" aria-labelledby="cryptpad-card-title">
        <header className="cryptpad-card__header">
          <img
            className="cryptpad-card__mark"
            src={cryptpadMarkUrl}
            alt=""
            aria-hidden="true"
          />
          <div className="cryptpad-card__brand">
            <p className="cryptpad-card__eyebrow">Federated workspace</p>
            <h1 id="cryptpad-card-title">CryptPad</h1>
          </div>
        </header>

        <p className="cryptpad-card__lead">
          Secure collaborative documents for certificate-backed Deploy App users.
        </p>

        <dl className="cryptpad-card__details">
          <div>
            <dt>Signed in as</dt>
            <dd>{card.callsign}</dd>
          </div>
          <div>
            <dt>Sandbox origin</dt>
            <dd>{data.sandbox_url}</dd>
          </div>
        </dl>

        <div className="cryptpad-card__actions">
          <a className="cryptpad-card__button" href={loginUrl}>
            Open CryptPad
          </a>
        </div>
      </section>
    </main>
  );
}
