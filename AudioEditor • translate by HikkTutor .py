#   Coded by D4n1l3k300    #
#     t.me/D4n13l3k00      #
# This code under AGPL-3.0 #

# requires: pydub numpy requests

# traslate by t.me/hikktutor #

import io
import math
import re

import numpy as np
import requests
from pydub import AudioSegment, effects
from telethon import types

from .. import loader, utils


@loader.tds
class AudioEditorMod(loader.Module):
    """Модуль для работы с звуком"""
    strings = {
        "name": "AudioEditor",
        "downloading": "<b>[{}]</b> Загрузка...",
        "working": "<b>[{}]</b> Работает...",
        "exporting": "<b>[{}]</b> Экспорт...",
        "set_value": "<b>[{}]</b> Specify the level from {} to {}...",
        "reply": "<b>[{}]</b> Ответ на аудио...",
        "set_fmt": "<b>[{}]</b> Specify the format of output audio...",
        "set_time": "<b>[{}]</b> Specify the time in the format start(мс):end(мс)"
    }

    async def basscmd(self, m):
        """.bass [Уровень басса 2-100 (Стандартно 2)] <Ответ на аудио>
        BassBoost"""
        args = utils.get_args_raw(m)
        if not args:
            lvl = 2.0
        else:
            if re.match(r'^\d+(\.\d+){0,1}$', args) and (1.0 < float(args) < 100.1):
                lvl = float(args)
            else:
                return await utils.answer(m, self.strings("set_value", m).format('BassBoost', 2.0, 100.0))
        audio = await get_audio(self, m, "BassBoost")
        if not audio:
            return
        sample_track = list(audio.audio.get_array_of_samples())
        out = (audio.audio - 0).overlay(audio.audio.low_pass_filter(int(round((3 *
                                                                               np.std(sample_track) / (math.sqrt(2)) - np.mean(sample_track)) * 0.005))) + lvl)
        await go_out(m, audio, out, audio.pref, f"{audio.pref} {lvl}lvl")

    async def fvcmd(self, m):
        """.fv [Уровень 2-100 (Стандартно 25)] <Ответ на аудио>
        Distort"""
        args = utils.get_args_raw(m)
        if not args:
            lvl = 25.0
        else:
            if re.match(r'^\d+(\.\d+){0,1}$', args) and (1.0 < float(args) < 100.1):
                lvl = float(args)
            else:
                return await utils.answer(m, self.strings("set_value", m).format('Distort', 2.0, 100.0))
        audio = await get_audio(self, m, "Distort")
        if not audio:
            return
        out = audio.audio + lvl
        await go_out(m, audio, out, audio.pref, f"{audio.pref} {lvl}lvl")

    async def echoscmd(self, m):
        """.echos <Ответ на аудио>
            Эхо эффект"""
        audio = await get_audio(self, m, "echo")
        if not audio:
            return
        out = AudioSegment.empty()
        n = 200
        none = io.BytesIO()
        out += audio.audio + AudioSegment.from_file(none)
        for i in range(5):
            echo = audio.audio - 10
            out = out.overlay(audio.audio, n)
            n += 200
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def volupcmd(self, m):
        """.volup <Ответ на аудио>
            Громче на 10dB"""
        audio = await get_audio(self, m, "+10dB")
        if not audio:
            return
        out = audio.audio + 10
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def voldwcmd(self, m):
        """.voldw <Ответ на аудио>
            Тише на 10dB"""
        audio = await get_audio(self, m, "-10dB")
        if not audio:
            return
        out = audio.audio - 10
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def revscmd(self, m):
        """.revs <Ответ на аудио>
            Развернуть звук"""
        audio = await get_audio(self, m, "Reverse")
        if not audio:
            return
        out = audio.audio.reverse()
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def repscmd(self, m):
        """.reps <Ответ на аудио>
            Repeat audio 2 times"""
        audio = await get_audio(self, m, "Repeat")
        if not audio:
            return
        out = audio.audio * 2
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def slowscmd(self, m):
        """.slows <Ответ на аудио>
            Замедлить до 0.5x"""
        audio = await get_audio(self, m, "SlowDown")
        if not audio:
            return
        s2 = audio.audio._spawn(audio.audio.raw_data, overrides={
            "frame_rate": int(audio.audio.frame_rate * 0.5)})
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await go_out(audio.message, audio, out, audio.pref, audio.pref, audio.duration * 2)

    async def fastscmd(self, m):
        """.fasts <Ответ на аудио >
        Ускорить в 1.5x"""
        audio = await get_audio(self, m, "SpeedUp")
        if not audio:
            return
        s2 = audio.audio._spawn(audio.audio.raw_data, overrides={
            "frame_rate": int(audio.audio.frame_rate * 1.5)})
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await go_out(audio.message, audio, out, audio.pref, audio.pref,
                     round(audio.duration / 2))

    async def rightscmd(self, m):
        """.rights <Ответ на аудио>
            Звук в правом канале"""
        audio = await get_audio(self, m, "Right channel")
        if not audio:
            return
        out = effects.pan(audio.audio, +1.0)
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def leftscmd(self, m):
        """.lefts <Ответ на аудио>
            Звук в левом канале"""
        audio = await get_audio(self, m, "Left channel")
        if not audio:
            return
        out = effects.pan(audio.audio, -1.0)
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def normscmd(self, m):
        """.norms <Ответ на аудио>
            Нормализовать звук"""
        audio = await get_audio(self, m, "Normalization")
        if not audio:
            return
        out = effects.normalize(audio.audio)
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def tovscmd(self, m):
        """.tovs <Ответ на аудио>
            Преобразовать в голосовое сообщение"""
        f = utils.get_args_raw(m)
        audio = await get_audio(self, m, "Voice")
        if not audio:
            return
        audio.voice = True
        await go_out(audio.message, audio, audio.audio, audio.pref, audio.pref)

    async def convscmd(self, m):
        """.convs <Ответ на аудио> [Аудио формат (ex. `mp3`)]
            Конвертировать аудио в другой формат"""
        f = utils.get_args(m)
        if not f:
            return await utils.answer(m, self.strings("set_fmt", m).format('Converter'))
        audio = await get_audio(self, m, "Converter")
        if not audio:
            return
        await go_out(audio.message, audio, audio.audio, audio.pref, f"Converted to {f[0].lower()}", fmt=f[0].lower())

    async def byrobertscmd(self, m):
        '''.byroberts <Ответ на аудио>
            Добавить концовку'''
        audio = await get_audio(self, m, "Directed by...")
        if not audio:
            return
        out = audio.audio + AudioSegment.from_file(io.BytesIO(requests.get(
            "https://raw.githubusercontent.com/D4n13l3k00/files-for-modules/master/directed.mp3").content)).apply_gain(
            +8)
        await go_out(audio.message, audio, out, audio.pref, audio.pref)

    async def cutscmd(self, m):
        """.cuts <Старт(мс):стоп(мс)> <Повторить аудио>
        Cut audio"""
        args = utils.get_args_raw(m)
        if not args:
            return await utils.answer(m, self.strings("set time", m).format('Cut'))
        r = re.compile(r'^(?P<start>\d+){0,1}:(?P<end>\d+){0,1}$')
        ee = r.match(args)
        if not ee:
            return await utils.answer(m, self.strings("set_time", m).format('Cut'))
        start = int(ee.group('start')) if ee.group('start') else 0
        end = int(ee.group('end')) if ee.group('end') else 0
        audio = await get_audio(self, m, "Cut")
        if not audio:
            return
        out = audio.audio[start:end if end else len(audio.audio)-1]
        await go_out(audio.message, audio, out, audio.pref, audio.pref)


async def get_audio(self, m, pref):
    class audio_ae_class():
        audio = None
        message = None
        duration = None
        voice = None
        pref = None
        reply = None
    r = await m.get_reply_message()
    if r and r.file and r.file.mime_type.split("/")[0] in ["audio", "video"]:
        ae = audio_ae_class()
        ae.pref = pref
        ae.reply = r
        ae.voice = r.document.attributes[0].voice if r.file.mime_type.split(
            "/")[0] == "audio" else False
        ae.duration = r.document.attributes[0].duration
        ae.message = await utils.answer(m, self.strings("downloading", m).format(pref))
        ae.audio = AudioSegment.from_file(
            io.BytesIO(await r.download_media(bytes)))
        ae.message = await utils.answer(ae.message, self.strings("working", m).format(pref))
        return ae
    await utils.answer(m, self.strings("reply", m).format(pref))
    return None


async def go_out(m, audio, out, pref, title, fs=None, fmt='mp3'):
    o = io.BytesIO()
    o.name = "аудио." + ("ogg" if audio.voice else "mp3")
    if audio.voice:
        out.split_to_mono()
    m = await utils.answer(m, AudioEditorMod.strings["exporting"].format(pref))
    out.export(o, format="ogg" if audio.voice else fmt,
               bitrate="64k" if audio.voice else None,
               codec="libopus" if audio.voice else None)
    o.seek(0)
    await utils.answer(m, o, reply_to=audio.reply.id,
                       voice_note=audio.voice, attributes=[
                           types.DocumentAttributeAudio(duration=fs if fs else audio.duration,
                                                        title=title,
                                                        performer="AudioEditor")] if not audio.voice else None)