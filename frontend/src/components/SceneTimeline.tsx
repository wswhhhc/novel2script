import { useMemo } from "react";
import { Clock, MapPin, Users } from "lucide-react";
import "./SceneTimeline.css";

interface Scene {
  id: string;
  title: string;
  location?: string;
  time?: string;
  characters?: string[];
  source_chapters?: string[];
  purpose?: string;
  summary?: string;
}

interface SceneTimelineProps {
  scenes: Scene[];
  characters?: Array<{ id: string; name: string }>;
}

export function SceneTimeline({ scenes, characters = [] }: SceneTimelineProps) {
  const characterMap = useMemo(() => {
    const map = new Map<string, string>();
    characters.forEach((char) => map.set(char.id, char.name));
    return map;
  }, [characters]);

  if (!scenes || scenes.length === 0) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
        暂无场景数据
      </div>
    );
  }

  return (
    <div className="scene-timeline">
      <div className="timeline-container">
        {scenes.map((scene, index) => (
          <div key={scene.id} className="timeline-item">
            <div className="timeline-marker">
              <div className="timeline-dot">{index + 1}</div>
              {index < scenes.length - 1 && <div className="timeline-line" />}
            </div>

            <div className="timeline-content">
              <div className="scene-card">
                <div className="scene-header">
                  <h3 className="scene-title">
                    {scene.id} - {scene.title}
                  </h3>
                  {scene.source_chapters && scene.source_chapters.length > 0 && (
                    <span className="scene-badge">
                      {scene.source_chapters.join(", ")}
                    </span>
                  )}
                </div>

                <div className="scene-meta">
                  {scene.time && (
                    <div className="scene-meta-item">
                      <Clock className="icon" size={16} />
                      <span>{scene.time}</span>
                    </div>
                  )}

                  {scene.location && (
                    <div className="scene-meta-item">
                      <MapPin className="icon" size={16} />
                      <span>{scene.location}</span>
                    </div>
                  )}

                  {scene.characters && scene.characters.length > 0 && (
                    <div className="scene-meta-item">
                      <Users className="icon" size={16} />
                      <span>
                        {scene.characters
                          .map((charId) => characterMap.get(charId) || charId)
                          .join(", ")}
                      </span>
                    </div>
                  )}
                </div>

                {scene.purpose && (
                  <div className="scene-purpose">
                    <strong>目的：</strong>
                    {scene.purpose}
                  </div>
                )}

                {scene.summary && (
                  <div className="scene-summary">{scene.summary}</div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
