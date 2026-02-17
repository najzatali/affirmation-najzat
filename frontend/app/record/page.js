"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { apiBase, apiDelete, apiGet, apiPost } from "../../lib/api";
import { i18n } from "../../lib/i18n";
import { patchHistory, pushHistory, readSession, saveSession } from "../../lib/studioStorage";

function formatDuration(seconds, lang) {
  if (seconds === 30) return lang === "ru" ? "30 сек" : "30 sec";
  return `${Math.floor(seconds / 60)} ${lang === "ru" ? "мин" : "min"}`;
}

export default function RecordPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  const [session, setSession] = useState(null);
  const [textValue, setTextValue] = useState("");

  const [voiceMode, setVoiceMode] = useState("system_voice");
  const [consent, setConsent] = useState(false);

  const [voices, setVoices] = useState([]);
  const [voiceId, setVoiceId] = useState("jane");

  const [music, setMusic] = useState([]);
  const [musicId, setMusicId] = useState("calm-1");

  const [packages, setPackages] = useState([]);
  const [purchases, setPurchases] = useState([]);
  const [durationSec, setDurationSec] = useState(30);
  const [deleteAfterDownload, setDeleteAfterDownload] = useState(true);

  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [recording, setRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [recordedUrl, setRecordedUrl] = useState("");
  const [voiceUploaded, setVoiceUploaded] = useState(false);

  const [jobId, setJobId] = useState("");
  const [jobStatus, setJobStatus] = useState("");
  const [jobError, setJobError] = useState("");
  const [resultUrl, setResultUrl] = useState("");

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const previewRef = useRef(null);
  const pollRef = useRef(null);

  const selectedPackage = useMemo(
    () => packages.find((item) => item.duration_sec === durationSec) || null,
    [packages, durationSec]
  );

  const selectedPurchase = useMemo(
    () => purchases.find((item) => item.duration_sec === durationSec && item.status === "paid" && !item.consumed) || null,
    [purchases, durationSec]
  );

  useEffect(() => {
    const current = readSession();
    setSession(current);
    if (current?.affirmations?.length) {
      setTextValue(current.affirmations.join("\n"));
    }
  }, []);

  useEffect(() => {
    async function bootstrap() {
      try {
        const [voiceData, musicData, packageData, purchaseData] = await Promise.all([
          apiGet("/api/voices"),
          apiGet("/api/music"),
          apiGet("/api/billing/packages"),
          apiGet("/api/billing/purchases"),
        ]);

        setVoices(Array.isArray(voiceData) ? voiceData : []);
        setMusic(Array.isArray(musicData) ? musicData : []);
        setPackages(Array.isArray(packageData) ? packageData : []);
        setPurchases(Array.isArray(purchaseData) ? purchaseData : []);
      } catch (e) {
        setError(String(e?.message || t.common.errorDefault));
      }
    }

    bootstrap();
  }, [t.common.errorDefault]);

  useEffect(() => {
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
      }
      if (previewRef.current) {
        previewRef.current.pause();
      }
      if (recordedUrl) {
        URL.revokeObjectURL(recordedUrl);
      }
    };
  }, [recordedUrl]);

  async function refreshPurchases() {
    try {
      const data = await apiGet("/api/billing/purchases");
      setPurchases(Array.isArray(data) ? data : []);
    } catch (_e) {
      // optional
    }
  }

  async function playPreview(relativeUrl) {
    try {
      if (previewRef.current) {
        previewRef.current.pause();
      }
      const audio = new Audio(`${apiBase()}${relativeUrl}`);
      previewRef.current = audio;
      await audio.play();
    } catch (_e) {
      setError(t.common.errorDefault);
    }
  }

  async function startRecording() {
    setError("");
    setSuccess("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);
        setRecordedBlob(blob);
        setRecordedUrl(url);
        setVoiceUploaded(false);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
    } catch (_e) {
      setError(t.common.errorDefault);
    }
  }

  function stopRecording() {
    if (!mediaRecorder) return;
    mediaRecorder.stop();
    setRecording(false);
  }

  async function uploadVoiceSample() {
    if (!recordedBlob) {
      setError(t.record.needVoiceUpload);
      return;
    }
    if (!consent) {
      setError(t.record.needConsent);
      return;
    }

    setBusy(true);
    setError("");
    setSuccess("");

    try {
      const form = new FormData();
      form.append("consent", "true");
      form.append("file", recordedBlob, "sample.webm");

      const response = await fetch(`${apiBase()}/api/voice-samples`, {
        method: "POST",
        body: form,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data?.detail || t.common.errorDefault);
      }

      setVoiceUploaded(true);
      setSuccess(t.record.voiceUploaded);
    } catch (e) {
      setError(String(e?.message || t.common.errorDefault));
    } finally {
      setBusy(false);
    }
  }

  async function createPurchase() {
    setBusy(true);
    setError("");
    setSuccess("");

    try {
      await apiPost("/api/billing/purchases", {
        duration_sec: durationSec,
        success_url: `${window.location.origin}/billing/success`,
        cancel_url: `${window.location.origin}/billing/cancel`,
      });
      await refreshPurchases();
      setSuccess(lang === "ru" ? "Пакет активирован" : "Package activated");
    } catch (e) {
      setError(String(e?.message || t.common.errorDefault));
    } finally {
      setBusy(false);
    }
  }

  async function createAudio() {
    setError("");
    setSuccess("");
    setJobError("");

    const text = textValue
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .join("\n");

    if (!text) {
      setError(t.record.noText);
      return;
    }

    if (!musicId) {
      setError(t.record.needMusic);
      return;
    }

    if (!durationSec) {
      setError(t.record.needDuration);
      return;
    }

    if (voiceMode === "system_voice" && !voiceId) {
      setError(t.record.needSystemVoice);
      return;
    }

    if (voiceMode === "my_voice") {
      if (!consent) {
        setError(t.record.needConsent);
        return;
      }
      if (!voiceUploaded) {
        setError(t.record.needVoiceUpload);
        return;
      }
    }

    if (durationSec > 30 && !selectedPurchase) {
      setError(t.record.paywall);
      return;
    }

    const projectId = session?.projectId;
    if (!projectId) {
      setError(t.record.noText);
      return;
    }

    setBusy(true);
    try {
      const job = await apiPost("/api/jobs", {
        project_id: projectId,
        affirmation_text: text,
        music_track_id: musicId,
        duration_sec: durationSec,
        voice_mode: voiceMode,
        preset_voice_id: voiceMode === "system_voice" ? voiceId : null,
        purchase_id: selectedPurchase?.id || null,
      });

      setJobId(job.id);
      setJobStatus(job.status || "queued");
      setResultUrl("");

      if (pollRef.current) clearInterval(pollRef.current);
      pollRef.current = setInterval(async () => {
        try {
          const status = await apiGet(`/api/jobs/${job.id}`);
          setJobStatus(status.status || "queued");

          if (status.status === "completed") {
            const stableUrl = `${apiBase()}/api/jobs/${job.id}/result?delete_after_download=false`;
            setResultUrl(stableUrl);
            clearInterval(pollRef.current);

            patchHistory(
              (item) => item.projectId === projectId,
              {
                status: "completed",
                jobId: job.id,
                resultUrl: stableUrl,
                durationSec,
              }
            );

            pushHistory({
              id: `${Date.now()}`,
              createdAt: new Date().toISOString(),
              areas: session?.areas || [],
              status: "completed",
              durationSec,
              language: lang,
              projectId,
              jobId: job.id,
              resultUrl: stableUrl,
              affirmations: text.split("\n"),
            });
          }

          if (status.status === "failed") {
            setJobError(status.error || t.common.errorDefault);
            clearInterval(pollRef.current);
          }
        } catch (_e) {
          setJobError(t.common.errorDefault);
          clearInterval(pollRef.current);
        }
      }, 2200);
    } catch (e) {
      setError(String(e?.message || t.common.errorDefault));
    } finally {
      setBusy(false);
    }
  }

  async function deleteVoiceData() {
    setError("");
    setSuccess("");

    try {
      await apiDelete("/api/privacy/voice");
      setVoiceUploaded(false);
      setSuccess(t.record.removeVoiceDone);
    } catch (e) {
      setError(String(e?.message || t.common.errorDefault));
    }
  }

  function openDownload() {
    if (!jobId) return;
    const url = `${apiBase()}/api/jobs/${jobId}/result?delete_after_download=${deleteAfterDownload ? "true" : "false"}`;
    window.open(url, "_blank", "noopener,noreferrer");
  }

  if (!session || !textValue) {
    return (
      <main className="page-shell">
        <AppNav title={t.record.title} subtitle={t.record.subtitle} />
        <section className="card">
          <p>{t.record.noText}</p>
          <a href="/onboarding" className="btn" style={{ marginTop: 10 }}>
            {t.record.toOnboarding}
          </a>
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <AppNav title={t.record.title} subtitle={t.record.subtitle} />

      <section className="card">
        <h2>{t.record.sourceText}</h2>
        <textarea className="textarea" value={textValue} onChange={(event) => setTextValue(event.target.value)} />
      </section>

      <section className="card">
        <h2>{t.record.voiceMode}</h2>
        <div className="mode-row">
          <button
            type="button"
            className={voiceMode === "system_voice" ? "mode-btn active" : "mode-btn"}
            onClick={() => setVoiceMode("system_voice")}
          >
            {t.record.voiceSystem}
          </button>
          <button
            type="button"
            className={voiceMode === "my_voice" ? "mode-btn active" : "mode-btn"}
            onClick={() => setVoiceMode("my_voice")}
          >
            {t.record.voiceMine}
          </button>
        </div>
      </section>

      {voiceMode === "my_voice" && (
        <section className="card">
          <h2>{t.record.voiceMine}</h2>
          <p className="muted">{t.record.recordHelp}</p>

          <article className="recorder-box">
            <h3>{t.record.sampleScriptTitle}</h3>
            <p>{t.record.sampleScript}</p>

            <div className="hero-actions">
              {!recording ? (
                <button type="button" className="btn" onClick={startRecording}>
                  {t.record.startRecording}
                </button>
              ) : (
                <button type="button" className="btn-secondary" onClick={stopRecording}>
                  {t.record.stopRecording}
                </button>
              )}

              {recording ? (
                <span className="warning">
                  <span className="recording-dot" />
                  {t.record.recording}
                </span>
              ) : null}
            </div>

            {recordedUrl ? (
              <div style={{ marginTop: 10 }}>
                <p className="footnote">{t.record.playback}</p>
                <audio controls src={recordedUrl} style={{ width: "100%" }} />
              </div>
            ) : null}
          </article>

          <label style={{ display: "flex", gap: 8, marginTop: 10 }}>
            <input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} />
            <span>{t.record.consentLabel}</span>
          </label>

          <div className="hero-actions">
            <button type="button" className="btn" onClick={uploadVoiceSample} disabled={busy}>
              {t.record.uploadVoice}
            </button>
            <button type="button" className="btn-ghost" onClick={deleteVoiceData}>
              {t.record.removeVoiceData}
            </button>
          </div>
        </section>
      )}

      {voiceMode === "system_voice" && (
        <section className="card">
          <h2>{t.record.systemVoices}</h2>
          <div className="catalog-grid">
            {voices.map((item) => {
              const title = lang === "ru" ? item.label_ru : item.label_en;
              const active = voiceId === item.id;
              return (
                <article key={item.id} className={active ? "catalog-item active" : "catalog-item"}>
                  <strong>{title}</strong>
                  <span className="muted">{item.gender}</span>
                  <div className="hero-actions" style={{ marginTop: 0 }}>
                    <button type="button" className="btn-ghost" onClick={() => playPreview(item.preview_url)}>
                      {t.record.previewVoice}
                    </button>
                    <button type="button" className="btn" onClick={() => setVoiceId(item.id)}>
                      {lang === "ru" ? "Выбрать" : "Select"}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}

      <section className="card">
        <h2>{t.record.musicTitle}</h2>
        <div className="catalog-grid">
          {music.map((item) => {
            const title = lang === "ru" ? item.title_ru : item.title_en;
            const active = musicId === item.id;
            return (
              <article key={item.id} className={active ? "catalog-item active" : "catalog-item"}>
                <strong>{title}</strong>
                <span className="muted">{item.mood}</span>
                <div className="hero-actions" style={{ marginTop: 0 }}>
                  <button type="button" className="btn-ghost" onClick={() => playPreview(item.preview_url)}>
                    {t.record.previewMusic}
                  </button>
                  <button type="button" className="btn" onClick={() => setMusicId(item.id)}>
                    {lang === "ru" ? "Выбрать" : "Select"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="card">
        <h2>{t.record.durationTitle}</h2>
        <p className="muted">{t.record.durationHint}</p>
        <div className="pill-row">
          {packages.map((item) => (
            <button
              key={item.duration_sec}
              type="button"
              className={durationSec === item.duration_sec ? "area-pill active" : "area-pill"}
              onClick={() => setDurationSec(item.duration_sec)}
            >
              {formatDuration(item.duration_sec, lang)} - {item.price_rub === 0 ? t.common.demo : `${item.price_rub} ₽`}
            </button>
          ))}
        </div>

        <div className="hero-actions">
          <button type="button" className="btn-ghost" onClick={createPurchase} disabled={busy || durationSec === 30}>
            {t.record.createPurchase}
          </button>
          <button type="button" className="btn" onClick={createAudio} disabled={busy}>
            {busy ? t.record.creatingAudio : t.record.createAudio}
          </button>
        </div>

        {selectedPackage?.price_rub > 0 && !selectedPurchase ? <p className="warning">{t.record.paywall}</p> : null}
      </section>

      <section className="card player-card">
        <div className="row-between">
          <h2>{t.record.jobStatus}</h2>
          {jobStatus ? <span className={`status-pill ${jobStatus}`}>{jobStatus}</span> : null}
        </div>

        {jobStatus === "queued" || jobStatus === "processing" ? <p className="muted">{t.record.queueHint}</p> : null}
        {jobError ? <p className="error">{jobError}</p> : null}

        {resultUrl ? (
          <>
            <p className="success">{t.record.ready}</p>
            <audio controls src={resultUrl} style={{ width: "100%" }} />

            <label style={{ display: "flex", gap: 8, marginTop: 10 }}>
              <input
                type="checkbox"
                checked={deleteAfterDownload}
                onChange={(event) => setDeleteAfterDownload(event.target.checked)}
              />
              <span>{t.record.deleteAfterDownload}</span>
            </label>

            <div className="hero-actions">
              <button type="button" className="btn" onClick={openDownload}>
                {t.record.download}
              </button>
              <a className="btn-ghost" href={resultUrl} target="_blank" rel="noreferrer">
                {t.record.listenResult}
              </a>
            </div>
          </>
        ) : null}

        <p className="footnote">{t.record.aiFootnote}</p>
      </section>

      {error ? <p className="error">{error}</p> : null}
      {success ? <p className="success">{success}</p> : null}
    </main>
  );
}
