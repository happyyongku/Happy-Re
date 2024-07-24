package com.example.happyre.entity;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "keyword_emotion")
public class KeywordEmotionEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "keyword_emotion_id")
    private Integer keywordEmotionId;

    @Column(name="keyword_id")
    private Integer keywordId;

    @Column(name="emotion_id")
    private Integer emotionId;

}