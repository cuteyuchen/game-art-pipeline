import { _decorator, Component, Sprite, SpriteFrame } from 'cc';

const { ccclass, property } = _decorator;

@ccclass('GameArtSpriteSequenceClip')
export class GameArtSpriteSequenceClip {
    @property
    public id = '';

    @property({ type: [SpriteFrame] })
    public frames: SpriteFrame[] = [];

    @property({ type: [Number] })
    public durationsMs: number[] = [];

    @property
    public loop = false;
}

@ccclass('GameArtSpriteSequenceAnimator')
export class GameArtSpriteSequenceAnimator extends Component {
    @property({ type: Sprite })
    public target: Sprite | null = null;

    @property({ type: [GameArtSpriteSequenceClip] })
    public clips: GameArtSpriteSequenceClip[] = [];

    @property
    public defaultClip = '';

    private active: GameArtSpriteSequenceClip | null = null;
    private frameIndex = 0;
    private elapsedMs = 0;
    private playing = false;

    protected start(): void {
        if (!this.target) {
            this.target = this.getComponent(Sprite);
        }
        if (this.defaultClip) {
            this.play(this.defaultClip);
        }
    }

    protected update(deltaTime: number): void {
        if (!this.playing || !this.active || !this.target || this.active.frames.length === 0) {
            return;
        }

        this.elapsedMs += deltaTime * 1000;
        let duration = this.frameDurationMs(this.active, this.frameIndex);
        while (this.elapsedMs >= duration && this.playing && this.active) {
            this.elapsedMs -= duration;
            this.advanceFrame();
            if (!this.active) {
                return;
            }
            duration = this.frameDurationMs(this.active, this.frameIndex);
        }
    }

    public play(id: string): boolean {
        const clip = this.clips.find((item) => item.id === id);
        if (!clip || clip.frames.length === 0 || !this.target) {
            return false;
        }
        this.active = clip;
        this.frameIndex = 0;
        this.elapsedMs = 0;
        this.playing = true;
        this.target.spriteFrame = clip.frames[0];
        return true;
    }

    public stop(): void {
        this.playing = false;
    }

    public hasClip(id: string): boolean {
        return this.clips.some((item) => item.id === id && item.frames.length > 0);
    }

    private advanceFrame(): void {
        if (!this.active || !this.target) {
            this.playing = false;
            return;
        }
        const next = this.frameIndex + 1;
        if (next >= this.active.frames.length) {
            if (!this.active.loop) {
                this.playing = false;
                this.frameIndex = this.active.frames.length - 1;
                return;
            }
            this.frameIndex = 0;
        } else {
            this.frameIndex = next;
        }
        this.target.spriteFrame = this.active.frames[this.frameIndex];
    }

    private frameDurationMs(clip: GameArtSpriteSequenceClip, index: number): number {
        if (clip.durationsMs.length === clip.frames.length) {
            return Math.max(1, clip.durationsMs[index]);
        }
        if (clip.durationsMs.length > 0) {
            return Math.max(1, clip.durationsMs[0]);
        }
        return 100;
    }
}
